/**
 * -----------------------------------------------------------------------------
 * pnpm Installation Hooks
 * -----------------------------------------------------------------------------
 *
 * Purpose:
 *   Optional customization hooks for pnpm's dependency resolution process.
 *
 * This file is intentionally minimal.
 *
 * Add hooks only when deterministic repository-wide dependency
 * customization is required.
 *
 * Examples:
 *
 * - Override transitive dependency versions
 * - Inject missing dependencies
 * - Apply organization-wide package policies
 * - Normalize package metadata
 *
 * Documentation:
 *   https://pnpm.io/pnpmfile
 *
 * -----------------------------------------------------------------------------
 */

"use strict";

/**
 * @type {import("pnpm").Hooks}
 */
module.exports = {
    hooks: {
        /**
         * Invoked before dependency resolution.
         *
         * @param {import("pnpm").PackageManifest} packageManifest
         * @returns {import("pnpm").PackageManifest}
         */
        readPackage(packageManifest) {
            // -----------------------------------------------------------------
            // Example:
            //
            // if (packageManifest.dependencies?.react) {
            //     packageManifest.dependencies.react = "^19.0.0";
            // }
            // -----------------------------------------------------------------

            return packageManifest;
        },
    },
};
