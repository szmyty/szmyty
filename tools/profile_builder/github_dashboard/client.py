"""GitHub REST and GraphQL client helpers for the engineering dashboard."""

from __future__ import annotations

import json
from datetime import date, datetime
from email.message import Message
from typing import Any
from urllib import error, parse, request

_API_ROOT = "https://api.github.com"
_GRAPHQL_URL = "https://api.github.com/graphql"
_USER_AGENT = "szmyty-profile-builder/1.0"
_TIMEOUT = 20


class ProviderFailure(RuntimeError):
    """Raised when public GitHub data cannot be collected."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ResourceNotFoundError(ProviderFailure):
    """Raised when a GitHub resource returns HTTP 404."""


class RateLimitedError(ProviderFailure):
    """Raised when GitHub rate limits the request."""


class GitHubDashboardClient:
    """Minimal GitHub REST and GraphQL client for public dashboard data."""

    def __init__(self, token: str) -> None:
        if not token:
            raise ProviderFailure("GitHub GraphQL collection requires GITHUB_TOKEN.")
        self._token = token

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + self._token,
            "User-Agent": _USER_AGENT,
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _request_json(
        self,
        url: str,
        *,
        method: str = "GET",
        payload: dict[str, Any] | None = None,
    ) -> tuple[Any, Message]:
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
        req = request.Request(url, headers=self._headers(), data=data, method=method)
        try:
            with request.urlopen(req, timeout=_TIMEOUT) as response:  # noqa: S310
                body = response.read().decode("utf-8")
                return json.loads(body), response.headers
        except error.HTTPError as exc:
            retry_after = exc.headers.get("Retry-After")
            rate_limit_remaining = exc.headers.get("X-RateLimit-Remaining")
            if exc.code == 429 or (
                exc.code == 403
                and (retry_after is not None or rate_limit_remaining == "0")
            ):
                raise RateLimitedError(
                    f"GitHub API rate limited: HTTP {exc.code}",
                    status_code=exc.code,
                ) from exc
            if exc.code == 404:
                raise ResourceNotFoundError(
                    "GitHub resource not found: HTTP 404",
                    status_code=404,
                ) from exc
            raise ProviderFailure(
                f"GitHub API request failed: HTTP {exc.code}",
                status_code=exc.code,
            ) from exc
        except error.URLError as exc:
            raise ProviderFailure(f"GitHub API unavailable: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise ProviderFailure(f"GitHub API returned invalid JSON: {exc}") from exc

    @staticmethod
    def _parse_next_link(headers: Message) -> str | None:
        link_header = headers.get("Link")
        if not link_header:
            return None
        for part in link_header.split(","):
            chunks = [item.strip() for item in part.split(";")]
            if len(chunks) < 2:
                continue
            if (
                chunks[1] == 'rel="next"'
                and chunks[0].startswith("<")
                and chunks[0].endswith(">")
            ):
                return chunks[0][1:-1]
        return None

    def paginate_rest_list(self, url: str) -> list[dict[str, Any]]:
        """Collect all pages from a REST list endpoint."""
        items: list[dict[str, Any]] = []
        next_url = url
        while next_url:
            payload, headers = self._request_json(next_url)
            if not isinstance(payload, list):
                raise ProviderFailure("Unexpected REST list payload from GitHub API.")
            items.extend(item for item in payload if isinstance(item, dict))
            next_url = self._parse_next_link(headers)
        return items

    def fetch_public_repositories(self, username: str) -> list[dict[str, Any]]:
        params = parse.urlencode({"per_page": 100, "type": "owner", "sort": "updated"})
        url = f"{_API_ROOT}/users/{username}/repos?{params}"
        return [
            repo
            for repo in self.paginate_rest_list(url)
            if not repo.get("private", False) and not repo.get("fork", False)
        ]

    def fetch_org_public_repositories(self, org: str) -> list[dict[str, Any]]:
        """Fetch public repositories owned by an organization."""
        params = parse.urlencode({"per_page": 100, "type": "public", "sort": "updated"})
        url = f"{_API_ROOT}/orgs/{org}/repos?{params}"
        try:
            return [
                repo
                for repo in self.paginate_rest_list(url)
                if not repo.get("private", False) and not repo.get("fork", False)
            ]
        except ProviderFailure as exc:
            if isinstance(exc, ResourceNotFoundError):
                return []
            raise

    def fetch_repositories_for_owner(
        self,
        login: str,
        owner_type: str,
    ) -> list[dict[str, Any]]:
        """Dispatch to the correct endpoint based on owner type."""
        if owner_type == "organization":
            return self.fetch_org_public_repositories(login)
        return self.fetch_public_repositories(login)

    def fetch_repository(self, full_name: str) -> dict[str, Any] | None:
        """Fetch a single public repository by owner/name."""
        url = f"{_API_ROOT}/repos/{full_name}"
        try:
            payload, _ = self._request_json(url)
            if not isinstance(payload, dict):
                return None
            return payload
        except ProviderFailure as exc:
            if isinstance(exc, ResourceNotFoundError):
                return None
            raise

    def fetch_languages(self, languages_url: str) -> dict[str, int]:
        payload, _ = self._request_json(languages_url)
        if not isinstance(payload, dict):
            raise ProviderFailure(
                "Unexpected repository languages payload from GitHub API."
            )
        return {
            str(name): int(value)
            for name, value in payload.items()
            if isinstance(name, str)
        }

    def fetch_releases(self, full_name: str) -> list[dict[str, Any]]:
        params = parse.urlencode({"per_page": 100})
        url = f"{_API_ROOT}/repos/{full_name}/releases?{params}"
        try:
            return self.paginate_rest_list(url)
        except ProviderFailure as exc:
            if isinstance(exc, ResourceNotFoundError):
                return []
            raise

    @staticmethod
    def _parse_last_page(headers: Message) -> int | None:
        """Return the final page number from a GitHub pagination header."""
        link_header = headers.get("Link")
        if not link_header:
            return None
        for part in link_header.split(","):
            chunks = [item.strip() for item in part.split(";")]
            if len(chunks) < 2 or chunks[1] != 'rel="last"':
                continue
            target = chunks[0]
            if not (target.startswith("<") and target.endswith(">")):
                continue
            query = parse.parse_qs(parse.urlparse(target[1:-1]).query)
            page = query.get("page", [None])[0]
            if isinstance(page, str) and page.isdigit():
                return int(page)
        return None

    def fetch_starred_repository_total(self, username: str) -> int:
        """Fetch an exact public starred-repository count in one REST request."""
        params = parse.urlencode({"per_page": 1})
        url = f"{_API_ROOT}/users/{username}/starred?{params}"
        payload, headers = self._request_json(url)
        if not isinstance(payload, list):
            raise ProviderFailure("Unexpected starred-repositories payload.")
        last_page = self._parse_last_page(headers)
        if last_page is not None:
            return last_page
        return len(payload)

    def fetch_contributions(
        self,
        username: str,
        *,
        window_start: date,
        window_end: date,
    ) -> dict[str, Any]:
        query = """
        query DashboardSnapshot($login: String!, $from: DateTime!, $to: DateTime!) {
          user(login: $login) {
            contributionsCollection(from: $from, to: $to) {
              totalCommitContributions
              totalIssueContributions
              totalPullRequestContributions
              totalPullRequestReviewContributions
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays {
                    contributionCount
                    contributionLevel
                    date
                    weekday
                  }
                }
              }
            }
          }
        }
        """
        payload, _ = self._request_json(
            _GRAPHQL_URL,
            method="POST",
            payload={
                "query": query,
                "variables": {
                    "login": username,
                    "from": datetime.combine(
                        window_start,
                        datetime.min.time(),
                    ).isoformat()
                    + "Z",
                    "to": datetime.combine(
                        window_end,
                        datetime.max.time(),
                    ).isoformat()
                    + "Z",
                },
            },
        )
        if not isinstance(payload, dict):
            raise ProviderFailure("Unexpected GraphQL payload from GitHub API.")
        errors = payload.get("errors")
        if errors:
            raise ProviderFailure(
                "GitHub GraphQL request failed for dashboard snapshot."
            )
        user = (payload.get("data") or {}).get("user")
        if not isinstance(user, dict):
            raise ProviderFailure("GitHub GraphQL user payload missing.")
        collection = user.get("contributionsCollection")
        if not isinstance(collection, dict):
            raise ProviderFailure("GitHub GraphQL contributions payload missing.")
        return collection
