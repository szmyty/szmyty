######################################################################
# Development container image
#
# This Dockerfile builds the image used by the VS Code devcontainer.
# It extends the official devcontainers base image and installs a
# collection of common build tools, language runtimes and utilities.
#
# The image is pinned to a specific digest so that builds are
# reproducible. Feel free to add or remove packages to suit your
# project's needs.
######################################################################
FROM mcr.microsoft.com/devcontainers/base:latest AS base

# Set safer shell options for script execution.
SHELL ["/bin/bash", "-o", "errexit", "-o", "errtrace", "-o", "functrace", "-o", "nounset", "-o", "pipefail", "-c"]

# TODO: Not sure what could go here.

FROM base AS environment

# Override the default temporary directory if needed. Useful when
# working on filesystems where /tmp has limited space.
ARG TMPDIR=/tmp

# Locale and timezone settings used during build and at runtime
ARG LANG=en_US.UTF-8
ARG LANGUAGE=en_US:en
ARG TZ=UTC
ARG LC_ALL=en_US.UTF-8

# Set workspace home directory
ENV WORKSPACE_HOME=/workspace

# Location where additional development utilities are installed
ENV UNIVERSAL_HOME=/opt/universal
ENV UNIVERSAL_BIN="${UNIVERSAL_HOME}/bin"
ENV UNIVERSAL_TOOLBOX="${UNIVERSAL_HOME}/toolbox"
ENV UNIVERSAL_CACHE="${UNIVERSAL_HOME}/cache"
ENV UNIVERSAL_LOGS="${UNIVERSAL_HOME}/logs"
ENV UNIVERSAL_CONFIG="${UNIVERSAL_HOME}/config"
ENV UNIVERSAL_LIB="${UNIVERSAL_HOME}/lib"
ENV UNIVERSAL_LOCKS="${UNIVERSAL_HOME}/locks"
ENV UNIVERSAL_FONTS="${UNIVERSAL_HOME}/fonts"
ENV UNIVERSAL_RUNTIME="${UNIVERSAL_HOME}/runtime"
ENV UNIVERSAL_APPS="${UNIVERSAL_HOME}/apps"
ENV UNIVERSAL_REPORTS="${UNIVERSAL_HOME}/reports"
ENV APT_CACHE_DIR="${UNIVERSAL_CACHE}/apt"

# Core environment variables for non-interactive apt operations and consistent Python behavior.
ENV DEBIAN_FRONTEND=noninteractive \
    DEBCONF_NONINTERACTIVE_SEEN=true \
    DEBIAN_PRIORITY=critical \
    DEBCONF_NOWARNINGS=yes \
    TERM=xterm-256color \
    APT_LISTCHANGES_FRONTEND=none \
    APT_LISTBUGS_FRONTEND=none \
    TMPDIR=${TMPDIR} \
    LANG=${LANG} \
    LANGUAGE=${LANGUAGE} \
    TZ=${TZ} \
    LC_ALL=${LC_ALL} \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    PYTHONUTF8=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_WARN_SCRIPT_LOCATION=on \
    PIP_DEFAULT_TIMEOUT=200 \
    PIP_ROOT_USER_ACTION=ignore \
    CARGO_TERM_COLOR=always \
    DO_NOT_TRACK=1 \
    PYTHONWARNINGS=default \
    CLICOLOR_FORCE=1 \
    CLICOLOR=1 \
    LESS=-R \
    COLORTERM=truecolor \
    GCC_COLORS="error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01" \
    FORCE_COLOR=1 \
    EDITOR=code \
    VISUAL=code \
    PAGER=less \
    GIT_PAGER=less

# XDG Base Directories: https://wiki.archlinux.org/title/XDG_Base_Directory
ENV XDG_CONFIG_HOME=${UNIVERSAL_CONFIG} \
    XDG_CACHE_HOME=${UNIVERSAL_CACHE} \
    XDG_DATA_HOME=${UNIVERSAL_TOOLBOX} \
    XDG_STATE_HOME=${UNIVERSAL_RUNTIME} \
    XDG_CONFIG_DIRS="${UNIVERSAL_CONFIG}:/etc/xdg"

# Add user application .desktop files to gnome.
# https://help.gnome.org/admin//system-admin-guide/2.32/menustructure-desktopentry.html.en
ENV XDG_DATA_DIRS="${UNIVERSAL_APPS}:/usr/local/share:/usr/share"

# Configuration options for various tools.
ENV ASDF_DIR="${XDG_DATA_HOME}/.asdf" \
    GEM_HOME="${XDG_DATA_HOME}/ruby/gems" \
    YARN_GLOBAL_FOLDER="${XDG_DATA_HOME}/yarn" \
    ANSIBLE_HOME="${XDG_DATA_HOME}/ansible" \
    FFMPEG_DATADIR="${XDG_DATA_HOME}/.ffmpeg" \
    GOPATH="${XDG_DATA_HOME}/go" \
    VS_CODE_DATA_DIR="${XDG_DATA_HOME}/vscode/data" \
    VS_CODE_EXTENSIONS_DIR="${XDG_DATA_HOME}/vscode/extensions" \
    PYENV_ROOT="${XDG_DATA_HOME}/.pyenv" \
    POETRY_HOME="${XDG_DATA_HOME}/.poetry" \
    PIPX_HOME="${XDG_DATA_HOME}/.pipx" \
    RBENV_ROOT="${XDG_DATA_HOME}/rbenv" \
    BUNDLE_USER_PLUGIN="${XDG_DATA_HOME}/bundle" \
    RUSTUP_HOME="${XDG_DATA_HOME}/rustup" \
    GRADLE_USER_HOME="${XDG_DATA_HOME}/.gradle" \
    FLUTTER_HOME="${XDG_DATA_HOME}/flutter" \
    OSH="${XDG_DATA_HOME}/oh-my-bash" \
    ZSH="${XDG_DATA_HOME}/oh-my-zsh" \
    GNUPGHOME="${XDG_DATA_HOME}/gnupg" \
    TERMINFO="${XDG_DATA_HOME}/terminfo" \
    M2_HOME="${XDG_DATA_HOME}/mvn/.mvn" \
    MINIKUBE_HOME="${XDG_DATA_HOME}/minikube" \
    WINEPREFIX="${XDG_DATA_HOME}/wine" \
    CCACHE_DIR="${XDG_DATA_HOME}/.ccache" \
    SINCE="${XDG_DATA_HOME}/since" \
    IPFS_PATH="${XDG_DATA_HOME}/ipfs" \
    NVM_DIR="${XDG_DATA_HOME}/.nvm" \
    PNPM_HOME="${XDG_DATA_HOME}/pnpm" \
    KERAS_HOME="${XDG_DATA_HOME}/keras" \
    R_HOME_USER="${XDG_DATA_HOME}/R" \
    ATOM_HOME="${XDG_DATA_HOME}/.atom" \
    KODI_DATA="${XDG_DATA_HOME}/kodi" \
    VAGRANT_HOME="${XDG_DATA_HOME}/vagrant" \
    CABAL_DIR="${XDG_DATA_HOME}/cabal" \
    AUDACITY_PATH="${XDG_DATA_HOME}/audacity" \
    BLENDER_USER_RESOURCES="${XDG_DATA_HOME}/blender" \
    DOTNET_CLI_HOME="${XDG_DATA_HOME}/dotnet" \
    ANALYZER_STATE_LOCATION_OVERRIDE="${XDG_DATA_HOME}/dart/.dartServer" \
    NUGET_PACKAGES="${XDG_DATA_HOME}/.nuget/packages" \
    MUJOCO_PY_MUJOCO_PATH="${XDG_DATA_HOME}/mujoco" \
    XMONAD_DATA_DIR="${XDG_DATA_HOME}/xmonad" \
    BINDLEPATH="${XDG_DATA_HOME}/bindle" \
    GQSTATE="${XDG_DATA_HOME}/gq/gq-state" \
    VLC_PLUGIN_PATH="${XDG_DATA_HOME}/vlc/plugins" \
    VLC_DATA_PATH="${XDG_DATA_HOME}/vlc/data" \
    ABOOK_DATA="${XDG_DATA_HOME}/abook/addressbook" \
    SDKMAN_DIR="${XDG_DATA_HOME}/sdkman" \
    PARALLEL_HOME="${XDG_DATA_HOME}/.parallel" \
    DISTCC_DIR="${XDG_DATA_HOME}/.distcc" \
    ZPLUG_HOME="${XDG_DATA_HOME}/zplug" \
    N_PREFIX="${XDG_DATA_HOME}/n" \
    UNISON="${XDG_DATA_HOME}/unison" \
    NB_DIR="${XDG_DATA_HOME}/nb" \
    OPAMROOT="${XDG_DATA_HOME}/opam" \
    PLATFORMIO_CORE_DIR="${XDG_DATA_HOME}/platformio" \
    IMAPFILTER_HOME="${XDG_DATA_HOME}/imapfilter" \
    ANKI_DIR="${XDG_DATA_HOME}/anki" \
    DOT_SAGE="${XDG_DATA_HOME}/sagemath/sage" \
    _Z_DATA="${XDG_DATA_HOME}/z" \
    BOGOFILTER_DIR="$XDG_DATA_HOME/bogofilter" \
    STACK_ROOT="${XDG_DATA_HOME}/stack" \
    TEXMACS_HOME_PATH="${XDG_DATA_HOME}/texmacs" \
    ELECTRUMDIR="${XDG_DATA_HOME}/.electrum" \
    GRIPHOME="${XDG_DATA_HOME}/grip" \
    EM_PORTS="${XDG_DATA_HOME}/emscripten/cache" \
    VOLTA_HOME="${XDG_DATA_HOME}/volta" \
    LEIN_HOME="${XDG_DATA_HOME}/lein" \
    FLATPAK_USER_DIR="${XDG_DATA_HOME}/flatpak" \
    LEDGER_FILE="${XDG_DATA_HOME}/hledger/.hledger.journal" \
    GETIPLAYERUSERPREFS="${XDG_DATA_HOME}/get_iplayer" \
    CRAWL_DIR="${XDG_DATA_HOME}/.crawl/" \
    GPODDER_DOWNLOAD_DIR="${XDG_DATA_HOME}/gpodder/downloads" \
    PEX_VERBOSE=0 \
    CALIBRE_SHOW_DEPRECATION_WARNINGS=0 \
    GHCUP_USE_XDG_DIRS="true" \
    MPV_VERBOSE="0" \
    MPV_LEAK_REPORT="0"

# Configure the ASDF version manager.
ENV ASDF_DATA_DIR="${ASDF_DIR}/data"
ENV ASDF_SHIMS_DIR="${ASDF_DATA_DIR}/shims"

ENV PIPX_BIN_DIR="${PIPX_HOME}/bin" \
    GOMODCACHE="${GOPATH}/pkg/mod" \
    TERMINFO_DIRS="${TERMINFO}:/usr/share/terminfo" \
    VAGRANT_ALIAS_FILE="${VAGRANT_HOME}/aliases"

# Set configuration files for various tools.
ENV ASDF_CONFIG_FILE="${XDG_CONFIG_HOME}/asdf/asdfrc" \
    CURLRC="${XDG_CONFIG_HOME}/curl/.curlrc" \
    WGETRC="${XDG_CONFIG_HOME}/wget/.wgetrc" \
    PIP_CONFIG_FILE="${XDG_CONFIG_HOME}/pip/pip.conf" \
    DOCKER_CONFIG="${XDG_CONFIG_HOME}/docker" \
    NPM_CONFIG_USERCONFIG="${XDG_CONFIG_HOME}/npm/.npmrc" \
    PYTHONSTARTUP="${XDG_CONFIG_HOME}/python/.pythonrc.py" \
    JUPYTER_CONFIG_DIR="${XDG_CONFIG_HOME}/jupyter" \
    IPYTHONDIR="${XDG_CONFIG_HOME}/.ipython" \
    AZURE_CONFIG_DIR="${XDG_CONFIG_HOME}/azure" \
    CALIBRE_TEMP_DIR="${TMPDIR}/calibre" \
    IDEA_PROPERTIES="${XDG_CONFIG_HOME}/intellij/idea.properties" \
    IDEA_VM_OPTIONS="${XDG_CONFIG_HOME}/intellij/idea.vmoptions" \
    ASPELL_CONF="per-conf ${XDG_CONFIG_HOME}/aspell/aspell.conf; personal ${XDG_CONFIG_HOME}/aspell/en.pws; repl ${XDG_CONFIG_HOME}/aspell/en.prepl" \
    PSQLRC="${XDG_CONFIG_HOME}/pg/psqlrc" \
    PGPASSFILE="${XDG_CONFIG_HOME}/pg/pgpass" \
    PGSERVICEFILE="${XDG_CONFIG_HOME}/pg/pg_service.conf" \
    CALIBRE_CONFIG_DIRECTORY="${XDG_CONFIG_HOME}/calibre" \
    XSEL_LOGFILE="${UNIVERSAL_LOGS}/xsel/.xsel.log" \
    ZDOTDIR="${XDG_CONFIG_HOME}/zsh" \
    BASH_COMPLETION_USER_FILE="${XDG_CONFIG_HOME}/bash-completion/bash_completion" \
    ACKRC="${XDG_CONFIG_HOME}/ack/.ackrc" \
    AWS_CONFIG_FILE="${XDG_CONFIG_HOME}/aws/config" \
    STARSHIP_CONFIG="${XDG_CONFIG_HOME}/starship.toml" \
    RIPGREP_CONFIG_PATH="${XDG_CONFIG_HOME}/ripgrep/config" \
    TRAVIS_CONFIG_PATH="${XDG_CONFIG_HOME}/travis" \
    OMNISHARPHOME="${XDG_CONFIG_HOME}/omnisharp" \
    DUB_HOME="${XDG_CONFIG_HOME}/dub" \
    EM_CONFIG="${XDG_CONFIG_HOME}/emscripten/config" \
    GR_PREFS_PATH="${XDG_CONFIG_HOME}/gnuradio" \
    TIGRC_USER="${XDG_CONFIG_HOME}/tig/tigrc" \
    XMONAD_CONFIG_DIR="${XDG_CONFIG_HOME}/xmonad" \
    GPODDER_HOME="${XDG_CONFIG_HOME}/gpodder" \
    IRBRC="${XDG_CONFIG_HOME}/irb/irbrc" \
    LYNX_CFG_PATH="${XDG_CONFIG_HOME}/lynx.cfg" \
    EASYOCR_MODULE_PATH="${XDG_CONFIG_HOME}/EasyOCR" \
    OCTAVE_SITE_INITFILE="${XDG_CONFIG_HOME}/octave/octaverc" \
    BUNDLE_USER_CONFIG="${XDG_CONFIG_HOME}/bundle" \
    DOT_SAGE="${XDG_CONFIG_HOME}/sage" \
    WEECHAT_HOME="${XDG_CONFIG_HOME}/weechat" \
    ABOOK_RC="${XDG_CONFIG_HOME}/.abook/abookrc" \
    DICTD_RC="${XDG_CONFIG_HOME}/.dictd/.dictrc" \
    GEF_RC="${XDG_CONFIG_HOME}/gef/.gef.rc" \
    CABAL_CONFIG="${XDG_CONFIG_HOME}/cabal/config" \
    RECOLL_CONFDIR="${XDG_CONFIG_HOME}/recoll" \
    KDEHOME="${XDG_CONFIG_HOME}/kde" \
    XINITRC="${XDG_CONFIG_HOME}/X11/xinitrc" \
    XSERVERRC="${XDG_CONFIG_HOME}/X11/xserverrc" \
    BINDLERC="${XDG_CONFIG_HOME}/bindlerc" \
    CONKY_CONFIG="${XDG_CONFIG_HOME}/conky/conkyrc" \
    CGDB_DIR="${XDG_CONFIG_HOME}/cgdb" \
    CLAWS_MAIL_CONFIG="${XDG_CONFIG_HOME}/claw-mails" \
    SVN_CONFIG_DIR="${XDG_CONFIG_HOME}/subversion" \
    CIN_CONFIG="${XDG_CONFIG_HOME}/cinelerra/bcast5" \
    FCEUX_HOME="${XDG_CONFIG_HOME}/fceux" \
    ELINKS_CONFDIR="${XDG_CONFIG_HOME}/elinks" \
    ELM_HOME="${XDG_CONFIG_HOME}/elm" \
    MOST_INITFILE="${XDG_CONFIG_HOME}/most/mostrc" \
    VIMPERATOR_RUNTIME="${XDG_CONFIG_HOME}/vimperator" \
    TS3_CONFIG_DIR="${XDG_CONFIG_HOME}/ts3client" \
    BOTO_CONFIG="${XDG_CONFIG_HOME}/boto" \
    VLCRC="${XDG_CONFIG_HOME}/vlc/vlcrc" \
    INPUTRC="${XDG_CONFIG_HOME}/readline/.inputrc" \
    GTK_RC_FILES="${XDG_CONFIG_HOME}/gtk-1.0/gtkrc" \
    GTK2_RC_FILES="${XDG_CONFIG_HOME}/gtk-2.0/gtkrc" \
    SCREENRC="${XDG_CONFIG_HOME}/screen/.screenrc" \
    NVIDIA_SETTINGS_RC="${XDG_CONFIG_HOME}/nvidia/.nvidia-settings-rc" \
    MPV_HOME="${XDG_CONFIG_HOME}/mpv" \
    NOTMUCH_CONFIG="${XDG_CONFIG_HOME}/notmuch/.notmuch-config" \
    UNCRUSTIFY_CONFIG="${XDG_CONFIG_HOME}/uncrustify/uncrustify.cfg" \
    MAXIMA_USERDIR="${XDG_CONFIG_HOME}/maxima" \
    K9SCONFIG="${XDG_CONFIG_HOME}/k9s" \
    NBRC_PATH="${XDG_CONFIG_HOME}/nbrc" \
    XCOMPOSEFILE="${XDG_CONFIG_HOME}/X11/xcompose" \
    MPLAYER_HOME="${XDG_CONFIG_HOME}/mplayer" \
    MEDNAFEN_HOME="${XDG_CONFIG_HOME}/mednafen" \
    MATHEMATICA_USERBASE="${XDG_CONFIG_HOME}/mathematica" \
    GQRC="${XDG_CONFIG_HOME}/gq/gqrc" \
    REDISCLI_RCFILE="${XDG_CONFIG_HOME}/redis/redisclirc" \
    NCMPC_CONFIG_DIR="${XDG_CONFIG_HOME}/ncmpc" \
    WAKATIME_HOME="${XDG_CONFIG_HOME}/wakatime" \
    CD_BOOKMARK_FILE="${XDG_CONFIG_HOME}/cd-bookmark/bookmarks" \
    DOOMDIR="${XDG_CONFIG_HOME}/doom" \
    R_PROFILE_USER="${XDG_CONFIG_HOME}/R/profile" \
    X3270PRO="${XDG_CONFIG_HOME}/x3270/config" \
    C3270PRO="${XDG_CONFIG_HOME}/c3270/config" \
    SINGULARITY_CONFIGDIR="${XDG_CONFIG_HOME}/singularity"

# Set cache directories for various tools.
ENV SONARLINT_USER_HOME="${XDG_CACHE_HOME}/.sonarlint" \
    NODE_COMPILER_CACHE="${XDG_CACHE_HOME}/node/compiler" \
    YARN_CACHE_FOLDER="${XDG_CACHE_HOME}/yarn" \
    PUB_CACHE="${XDG_CACHE_HOME}/.pub-cache" \
    __GL_SHADER_DISK_CACHE_PATH="${XDG_CACHE_HOME}/.nv" \
    HOMEBREW_CACHE="${XDG_CACHE_HOME}/homebrew" \
    KSCRIPT_CACHE_DIR="${XDG_CACHE_HOME}/kscript" \
    PYTHON_EGG_CACHE="${XDG_CACHE_HOME}/.python-eggs" \
    PEX_ROOT="${XDG_CACHE_HOME}/.pex" \
    MYPY_CACHE_DIR="${XDG_CACHE_HOME}/mypy" \
    CUDA_CACHE_PATH="${XDG_CACHE_HOME}/nv" \
    CALIBRE_CACHE_DIRECTORY="${XDG_CACHE_HOME}/calibre" \
    SOLARGRAPH_CACHE="${XDG_CACHE_HOME}/solargraph" \
    XCOMPOSECACHE="${XDG_CACHE_HOME}/X11/xcompose" \
    DVDCSS_CACHE="${XDG_CACHE_HOME}/dvdcss" \
    XMONAD_CACHE_DIR="${XDG_CACHE_HOME}/xmonad" \
    BUNDLE_USER_CACHE="${XDG_CACHE_HOME}/bundle" \
    GEM_SPEC_CACHE="${XDG_CACHE_HOME}/gem" \
    ICEAUTHORITY="${XDG_CACHE_HOME}/ICEauthority" \
    PYLINTHOME="${XDG_CACHE_HOME}/pylint" \
    STARSHIP_CACHE="${XDG_CACHE_HOME}/starship" \
    ALTUSERXSESSION="${XDG_CACHE_HOME}/X11/Xsession" \
    USERXSESSION="${XDG_CACHE_HOME}/X11/xsession" \
    USERXSESSIONRC="${XDG_CACHE_HOME}/X11/xsessionrc" \
    SINGULARITY_CACHEDIR="${XDG_CACHE_HOME}/singularity" \
    RUFF_CACHE_DIR="${XDG_CACHE_HOME}/ruff" \
    EM_CACHE="${XDG_CACHE_HOME}/emscripten/cache" \
    HOMEBREW_TEMP="${XDG_CACHE_HOME}/homebrew/tmp" \
    HOMEBREW_LOGS="${UNIVERSAL_LOGS}/homebrew"

# History settings
ENV HISTFILE="${XDG_CACHE_HOME}/bash_history" \
    HISTSIZE=10000 \
    NODE_REPL_HISTORY="${XDG_CACHE_HOME}/node_repl_history" \
    LESSHISTFILE="${XDG_CACHE_HOME}/less_history" \
    LESSHISTSIZE=10000 \
    REDISCLI_HISTFILE="${XDG_CACHE_HOME}/rediscli_history" \
    SQLITE_HISTORY="${XDG_CACHE_HOME}/sqlite_history" \
    PSQL_HISTORY="${XDG_CACHE_HOME}/psql_history" \
    PGSQL_HISTORY="${XDG_CACHE_HOME}/pgsql_history" \
    MYSQL_HISTFILE="${XDG_CACHE_HOME}/mysql_history" \
    MYSQL_HISTSIZE=10000 \
    CALCHISTFILE="${XDG_CACHE_HOME}/calc_history" \
    UNITS_HISTORY_FILE="${XDG_CACHE_HOME}/units_history" \
    RLWRAP_HOME="${XDG_CACHE_HOME}/rlwrap" \
    GDBHISTFILE="${XDG_CACHE_HOME}/gdb_history" \
    OCTAVE_HISTFILE="${XDG_CACHE_HOME}/octave-hsts" \
    JULIA_HISTORY="${XDG_CACHE_HOME}/julia_history" \
    R_HISTFILE="${XDG_CACHE_HOME}/R_history"

# Disable telemetry for various tools.
# https://github.com/beatcracker/toptout
ENV DO_NOT_TRACK=1 \
    ANALYTICS="no" \
    ADBLOCK="true" \
    DisableTelemetry="True" \
    TELEMETRY_ENABLED=0 \
    AZURE_CORE_COLLECT_TELEMETRY=0 \
    SAM_CLI_TELEMETRY=0 \
    GOTELEMETRY="off" \
    STNOUPGRADE=1 \
    YARN_ENABLE_TELEMETRY=false \
    NEXT_TELEMETRY_DISABLED=1 \
    GATSBY_TELEMETRY_DISABLED=1 \
    STORYBOOK_DISABLE_TELEMETRY=1 \
    DOTNET_CLI_TELEMETRY_OPTOUT=1 \
    DOTNET_EnableDiagnostics=0 \
    DOTNET_INTERACTIVE_CLI_TELEMETRY_OPTOUT=1 \
    MLDOTNET_CLI_TELEMETRY_OPTOUT="True" \
    DOTNET_SVCUTIL_TELEMETRY_OPTOUT=1 \
    CANVAS_LMS_STATS_COLLECTION="opt_out" \
    TELEMETRY_OPT_IN="" \
    ET_NO_TELEMETRY="ANY_VALUE" \
    WERF_TELEMETRY=0 \
    MSLAB_TELEMETRY_LEVEL="None" \
    ALLOW_UI_ANALYTICS="false" \
    NUKE_TELEMETRY_OPTOUT=1 \
    EARTHLY_DISABLE_ANALYTICS=1 \
    STRIPE_CLI_TELEMETRY_OPTOUT=1 \
    FEAST_TELEMETRY="False" \
    MELTANO_DISABLE_TRACKING="True" \
    QUILT_DISABLE_USAGE_METRICS="True" \
    CARBON_TELEMETRY_DISABLED=1 \
    FASTLANE_OPT_OUT_USAGE="YES" \
    GATSBY_TELEMETRY_DISABLED=1 \
    ORYX_DISABLE_TELEMETRY="true" \
    RASA_TELEMETRY_ENABLED="false" \
    CLOUDSDK_CORE_DISABLE_USAGE_REPORTING="true" \
    ALIBUILD_NO_ANALYTICS=1 \
    HOMEBREW_NO_ANALYTICS=1 \
    HOMEBREW_NO_ANALYTICS_THIS_RUN=1 \
    HOMEBREW_NO_AUTO_UPDATE=1 \
    DECK_ANALYTICS="off" \
    NG_CLI_ANALYTICS="false" \
    NG_CLI_ANALYTICS_SHARE="false" \
    INFLUXD_REPORTING_DISABLED="true" \
    MOBILE_CENTER_TELEMETRY="off" \
    ARDUINO_METRICS_ENABLED="false" \
    POWERSHELL_TELEMETRY_OPTOUT=1 \
    POWERSHELL_UPDATECHECK="Off" \
    LYNX_ANALYTICS=0 \
    DISABLE_QUICKWIT_TELEMETRY=1 \
    AUTOMAGICA_NO_TELEMETRY="1" \
    MM_LOGSETTINGS_ENABLEDIAGNOSTICS="false" \
    MM_SERVICESETTINGS_ENABLESECURITYFIXALERT="false" \
    APPCD_TELEMETRY=0 \
    BF_CLI_TELEMETRY="false" \
    DA_TEST_DISABLE_TELEMETRY=1 \
    CHOOSENIM_NO_ANALYTICS=1 \
    COCOAPODS_DISABLE_STATS="true" \
    CUBEJS_TELEMETRY="false" \
    HOOKDECK_CLI_TELEMETRY_OPTOUT=1 \
    VUEDX_TELEMETRY="off" \
    HINT_TELEMETRY="off" \
    BATECT_ENABLE_TELEMETRY="false" \
    DAGSTER_DISABLE_TELEMETRY=1 \
    TELEMETRY_DISABLED=1 \
    PROSE_TELEMETRY_OPTOUT=1 \
    SKU_TELEMETRY="false" \
    PANTS_ANONYMOUS_TELEMETRY_ENABLED="false" \
    CHECKPOINT_DISABLE=1 \
    ARM_DISABLE_TERRAFORM_PARTNER_ID="true" \
    SCOUT_DISABLE=1 \
    PULUMI_SKIP_UPDATE_CHECK="true" \
    DISABLE_CRASH_REPORT=1 \
    KICS_COLLECT_TELEMETRY=0 \
    INFRACOST_SELF_HOSTED_TELEMETRY="false" \
    INFRACOST_SKIP_UPDATE_CHECK="true" \
    DISABLE_AUTO_UPDATE="true" \
    BUGGER_OFF=1 \
    HASURA_GRAPHQL_ENABLE_TELEMETRY="false" \
    MEILI_NO_ANALYTICS="true" \
    NC_DISABLE_TELE=1 \
    ONE_CODEX_NO_TELEMETRY="True" \
    SQA_OPT_OUT="true" \
    ROCKSET_CLI_TELEMETRY_OPTOUT=1 \
    TUIST_STATS_OPT_OUT=1 \
    AUTOMATEDLAB_TELEMETRY_OPTIN=0 \
    AUTOMATEDLAB_TELEMETRY_OPTOUT=1 \
    CHEF_TELEMETRY_OPT_OUT=1 \
    DASH_DISABLE_TELEMETRY=1 \
    TYPO3_DISABLE_CORE_UPDATER=1 \
    REDIRECT_TYPO3_DISABLE_CORE_UPDATER=1 \
    IG_PRO_OPT_OUT="YES" \
    PNPPOWERSHELL_DISABLETELEMETRY="true" \
    PNPPOWERSHELL_UPDATECHECK="false" \
    SF_DISABLE_TELEMETRY="true" \
    APOLLO_TELEMETRY_DISABLED=1 \
    REPORTPORTAL_CLIENT_JS_NO_ANALYTICS="true" \
    SALTO_TELEMETRY_DISABLE=1 \
    VSTEST_TELEMETRY_OPTEDIN=0 \
    NUXT_TELEMETRY_DISABLED=1 \
    MSSQL_CLI_TELEMETRY_OPTOUT="True" \
    VAGRANT_CHECKPOINT_DISABLE=1 \
    VAGRANT_BOX_UPDATE_CHECK_DISABLE=1 \
    SFDX_DISABLE_TELEMETRY="true" \
    RESTLER_TELEMETRY_OPTOUT=1 \
    TEEM_DISABLE="true" \
    F5_ALLOW_TELEMETRY="false" \
    REACT_APP_WEBINY_TELEMETRY="false" \
    STRAPI_TELEMETRY_DISABLED="true" \
    STRAPI_DISABLE_UPDATE_NOTIFICATION="true" \
    SLS_TRACKING_DISABLED=1 \
    SLS_TELEMETRY_DISABLED=1 \
    SUGGESTIONS_OPT_OUT=1

# Node.js options for performance tuning and reporting
# https://nodejs.org/api/cli.html
ARG NODE_OPTIONS="\
  --max-old-space-size=4096 \
  --max-semi-space-size=512 \
  --report-directory=${UNIVERSAL_REPORTS}/node \
  --diagnostic-dir=${XDG_CACHE_HOME}/node/diagnostics \
"
ENV NODE_OPTIONS="${NODE_OPTIONS}"

# Taskfile installation directory
ENV TASKFILE_HOME_DIR="${UNIVERSAL_HOME}/.task"

# Prepend devtool locations to the PATH for easy access
ENV PATH="${UNIVERSAL_BIN}:${UNIVERSAL_BIN}/install:${UNIVERSAL_BIN}/tests:${UNIVERSAL_TOOLBOX}:${TASKFILE_HOME_DIR}:${ASDF_DIR}/bin:${ASDF_SHIMS_DIR}:${PATH}"

FROM environment AS shell

# Set working directory
WORKDIR ${WORKSPACE_HOME}

# Copy custom shell scripts and binaries
COPY --chown=vscode:vscode shell/bin/ ${UNIVERSAL_BIN}/
RUN chmod +x ${UNIVERSAL_BIN}/*

# COPY custom shell library
COPY --chown=vscode:vscode shell/lib/ ${UNIVERSAL_LIB}/
RUN find ${UNIVERSAL_LIB} -type f -name "*.sh" -exec chmod +x {} \;

# Copy configuration files for apt and dpkg
COPY shell/etc/dpkg/dpkg.cfg.d/*.conf /etc/dpkg/dpkg.cfg.d/
COPY shell/etc/apt/apt.conf.d/*.conf /etc/apt/apt.conf.d/

# Copy configuration files
COPY shell/config/wget/.wgetrc ${WGETRC}
COPY shell/config/curl/.curlrc ${CURLRC}
COPY shell/config/asdf/.asdfrc ${ASDF_CONFIG_FILE}
COPY shell/config/python/.pythonrc.py ${PYTHONSTARTUP}

# COPY shell/config/.gitignore_global

# Ensure GNUPG home exists with correct perms and ownership for vscode
RUN install -d -m 0700 -o vscode -g vscode "${GNUPGHOME}" \
 && chown -R vscode:vscode "${UNIVERSAL_TOOLBOX}"

FROM shell AS apt-packages

# Install common development tools and libraries
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=apt-cache \
    --mount=type=cache,target=/var/lib/apt,sharing=locked,id=apt-lib \
    apt-get update -qq && \
    apt-get upgrade --yes && \
    apt-get install --yes --no-install-recommends \
    ansible \
    apt-rdepends \
    bat \
    build-essential \
    ca-certificates \
    ccache \
    chktex \
    clang \
    clang-format \
    clang-tidy \
    cmake \
    cpanminus \
    curl \
    debtree \
    flac \
    apt-transport-https \
    direnv \
    dnsutils \
    dos2unix \
    exiftool \
    musepack-tools \
    wavpack \
    ffmpeg \
    rubberband-cli \
    libsoundtouch1 \
    ffmpegthumbnailer \
    soundstretch \
    file \
    fontconfig \
    fonts-lmodern \
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    fzf \
    gawk \
    gdal-bin \
    gettext \
    ghostscript \
    git \
    git-buildpackage \
    git-lfs \
    gnupg \
    graphviz \
    htop \
    id3v2 \
    inkscape \
    iputils-ping \
    jq \
    lame \
    less \
    libaudio2 \
    libavif-dev \
    libblosc-dev \
    libboost-all-dev \
    libbz2-dev \
    libcairo2-dev \
    libcurl4-openssl-dev \
    libdb-dev \
    libde265-dev \
    libev-dev \
    libexif-dev \
    libffi-dev \
    libgdal-dev \
    libgdbm-dev \
    libgeos-dev \
    libgif-dev \
    libheif-dev \
    libimagequant-dev \
    libjpeg-dev \
    libkrb5-dev \
    liblcms2-dev \
    liblz4-dev \
    liblzma-dev \
    libncurses-dev \
    libnss3-dev \
    libopenexr-dev \
    libopenjp2-7-dev \
    libpango1.0-dev \
    libperl-dev \
    libpng-dev \
    libproj-dev \
    libraw-dev \
    libreadline-dev \
    libsox-fmt-all \
    libspatialindex-dev \
    libsqlite3-dev \
    libssl-dev \
    libtiff-dev \
    libtool \
    libvips-dev \
    libwebp-dev \
    libxi-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libxslt1-dev \
    libzstd-dev \
    lintian \
    llvm \
    locales \
    locales-all \
    logrotate \
    lsb-release \
    lsof \
    piuparts \
    make \
    mediainfo \
    moreutils \
    nano \
    net-tools \
    netcat-openbsd \
    ninja-build \
    nmap \
    openssh-client \
    openssl \
    opus-tools \
    pandoc \
    parallel \
    pkg-config \
    potrace \
    procps \
    proj-bin \
    psmisc \
    pwgen \
    ripgrep \
    rsync \
    software-properties-common \
    sox \
    sqlite3 \
    strace \
    streamripper \
    sudo \
    sysdig \
    sysstat \
    tar \
    tcpdump \
    tini \
    tk-dev \
    tree \
    tzdata \
    unzip \
    uuid-dev \
    vim \
    vorbis-tools \
    watch \
    wget \
    xsel \
    xz-utils \
    yq \
    zlib1g-dev \
    zsh

######################################################################
# CPython (pinned global)
######################################################################
FROM apt-packages AS cpython

ARG PYTHON_VERSION=3.12.10
ARG PYTHON_TARBALL=Python-${PYTHON_VERSION}.tar.xz
ARG PYTHON_URL=https://www.python.org/ftp/python/${PYTHON_VERSION}/${PYTHON_TARBALL}
ARG PYTHON_SHA256=
ARG PYTHON_COMMIT=""
ARG PYTHON_REPO="https://github.com/python/cpython.git"

# final install prefix
ENV PY_PREFIX=${UNIVERSAL_TOOLBOX}/python/${PYTHON_VERSION}
ENV PATH="${PY_PREFIX}/bin:${PATH}"

# build deps (minimum set)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=apt-cache \
    --mount=type=cache,target=/var/lib/apt,sharing=locked,id=apt-lib \
    apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
      build-essential \
      curl \
      ca-certificates \
      git \
      xz-utils \
      tcl-dev tk-dev \
      libffi-dev \
      libbz2-dev \
      libgdbm-dev \
      libgdbm-compat-dev \
      liblzma-dev \
      libncursesw5-dev \
      libreadline-dev \
      libsqlite3-dev \
      libssl-dev \
      libexpat1-dev \
      zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/python-build

RUN set -Eeuo pipefail; \
    if [ -n "${PYTHON_COMMIT}" ]; then \
      echo "🐍 Cloning CPython repository from ${PYTHON_REPO}…"; \
      git init .; \
      git remote add origin "${PYTHON_REPO}"; \
      echo "📌 Fetching commit ${PYTHON_COMMIT}…"; \
      git fetch --depth 1 origin "${PYTHON_COMMIT}"; \
      git checkout --detach FETCH_HEAD; \
    else \
      echo "📥 Downloading CPython ${PYTHON_VERSION}…"; \
      curl -fsSL "${PYTHON_URL}" -o "${PYTHON_TARBALL}"; \
      if [ -n "${PYTHON_SHA256}" ]; then \
        echo "${PYTHON_SHA256}  ${PYTHON_TARBALL}" | sha256sum -c -; \
      else \
        echo "⚠️  PYTHON_SHA256 not provided; proceeding without checksum verification"; \
      fi; \
      tar -xJf "${PYTHON_TARBALL}" --strip-components=1; \
    fi; \
    ./configure \
      --prefix="${PY_PREFIX}" \
      --enable-optimizations \
      --with-lto \
      --with-ensurepip=install; \
    make -j"$(nproc)"; \
    make install; \
    ln -sf python3 "${PY_PREFIX}/bin/python"; \
    ln -sf pip3 "${PY_PREFIX}/bin/pip"; \
    "${PY_PREFIX}/bin/python3" --version; \
    "${PY_PREFIX}/bin/pip3" --version; \
    python --version; \
    pip --version; \
    cd / && rm -rf /tmp/python-build; \
    echo "✅ CPython ${PYTHON_VERSION} installed successfully at ${PY_PREFIX}."

FROM apt-packages AS rust

ARG RUSTUP_VERSION=1.28.2
ARG INSTALL_RUST=true

# Install Rust toolchain
ENV INSTALL_RUST="${INSTALL_RUST}" \
    RUSTUP_VERSION="${RUSTUP_VERSION}" \
    RUSTUP_HOME="${XDG_DATA_HOME}/rustup" \
    RUST_BACKTRACE=1 \
    CARGO_TERM_COLOR=always \
    CARGO_HOME="${XDG_DATA_HOME}/cargo"

ENV PATH="${CARGO_HOME}/bin:${PATH}"

# Install Rust using rustup
RUN bash -Eeuo pipefail -c '\
      if [[ "${INSTALL_RUST}" == "true" ]]; then \
        curl --proto '=https' --tlsv1.2 --silent --show-error --fail --location https://sh.rustup.rs | \
        bash -s -- --default-toolchain stable --profile complete --no-modify-path -y && \
        rustc --version && \
        cargo --version && \
        echo "✅ Rust toolchain installed successfully." \
      else \
        echo "📁 Skipping Rustup install"; \
      fi'

# Ensure dev user owns tool dirs for runtime installs
RUN install -d -m 0775 -o vscode -g vscode \
      "${CARGO_HOME}" "${CARGO_HOME}/bin" "${CARGO_HOME}/git" "${CARGO_HOME}/registry" "${RUSTUP_HOME}"

FROM rust AS oxipng

ARG INSTALL_OXIPNG=true
ARG OXIPNG_REPO=https://github.com/oxipng/oxipng.git
ARG OXIPNG_COMMIT=c7d462f909e9c6ebc8d32820d83a6119b681cad6

ENV INSTALL_OXIPNG=${INSTALL_OXIPNG} \
    OXIPNG_REPO=${OXIPNG_REPO} \
    OXIPNG_COMMIT=${OXIPNG_COMMIT}

RUN bash -Eeuo pipefail -c '\
      if [[ "${INSTALL_OXIPNG}" == "true" ]]; then \
        cargo install --git ${OXIPNG_REPO} oxipng --rev ${OXIPNG_COMMIT} --force && \
        oxipng --version && \
        echo "✅ oxipng installed successfully." \
      else \
        echo "📁 Skipping oxipng install"; \
      fi'

FROM oxipng AS lychee

ARG INSTALL_LYCHEE=true
ARG LYCHEE_REPO=https://github.com/lycheeverse/lychee.git
ARG LYCHEE_COMMIT=3592972d6462ceb6081c3945cc43121bc3ce2039

ENV INSTALL_LYCHEE=${INSTALL_LYCHEE} \
    LYCHEE_REPO=${LYCHEE_REPO} \
    LYCHEE_COMMIT=${LYCHEE_COMMIT}

RUN cargo install --git ${LYCHEE_REPO} lychee --rev ${LYCHEE_COMMIT} --force

FROM lychee AS eza

ARG INSTALL_EZA=true
ARG EZA_REPO=https://github.com/eza-community/eza
ARG EZA_COMMIT=7a2b2661148a3fa4f01bfe41e74c5f1c57a24bd6

ENV INSTALL_EZA=${INSTALL_EZA} \
    EZA_REPO=${EZA_REPO} \
    EZA_COMMIT=${EZA_COMMIT}

RUN cargo install --git ${EZA_REPO} eza --rev ${EZA_COMMIT} --force

FROM eza AS final2

FROM oxipng AS perl

######################################################################
# Perl toolchain + Language Server + dev tooling (toggleable)
######################################################################
ARG INSTALL_PERL=true
ARG INSTALL_PERL_DEVTOOLS=true

# System deps (same as your original; fail fast + clean up)
USER root
RUN bash -Eeuo pipefail -c '\
  apt-get update -qq && \
  apt-get install --yes --no-install-recommends \
    build-essential \
    perl \
    perl-base \
    perl-modules \
    libperl-dev \
    libio-aio-perl && \
  apt-get clean && rm -rf /var/lib/apt/lists/* \
'

# Ensure user-owned install prefix for CPAN
RUN install -d -m 0775 -o vscode -g vscode "${UNIVERSAL_TOOLBOX}/perl5"
# USER vscode

# Make your contained local::lib visible at build + runtime
ENV PERL5LIB="${UNIVERSAL_TOOLBOX}/perl5/lib/perl5${PERL5LIB:+:$PERL5LIB}" \
    PATH="${UNIVERSAL_TOOLBOX}/perl5/bin:${PATH}"

# CPAN modules installed into your custom directory; fail on error; smoke test
RUN bash -Eeuo pipefail -c "\
  cpanm --no-interactive --local-lib-contained \"${UNIVERSAL_TOOLBOX}/perl5\" \
    AnyEvent::AIO IO::AIO Perl::LanguageServer && \
  perl -MPerl::LanguageServer -e 'print qq(Perl::LanguageServer OK\n)' \
"

FROM perl AS gcloud

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=apt-cache \
    --mount=type=cache,target=/var/lib/apt,sharing=locked,id=apt-lib \
    bash -Eeuo pipefail -c '\
      echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
        | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
      curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
        | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
      apt-get update -qq && \
      apt-get install -y --no-install-recommends \
        google-cloud-cli \
        google-cloud-cli-anthos-auth \
        google-cloud-cli-app-engine-go \
        google-cloud-cli-app-engine-grpc \
        google-cloud-cli-app-engine-java \
        google-cloud-cli-app-engine-python \
        google-cloud-cli-app-engine-python-extras \
        google-cloud-cli-bigtable-emulator \
        google-cloud-cli-cbt \
        google-cloud-cli-cloud-build-local \
        google-cloud-cli-cloud-run-proxy \
        google-cloud-cli-config-connector \
        google-cloud-cli-datastore-emulator \
        google-cloud-cli-firestore-emulator \
        google-cloud-cli-gke-gcloud-auth-plugin \
        google-cloud-cli-kpt \
        google-cloud-cli-kubectl-oidc \
        google-cloud-cli-local-extract \
        google-cloud-cli-minikube \
        google-cloud-cli-nomos \
        google-cloud-cli-pubsub-emulator \
        google-cloud-cli-skaffold \
        google-cloud-cli-spanner-emulator \
        google-cloud-cli-terraform-validator \
        google-cloud-cli-tests \
        kubectl \
    '

FROM apt-packages AS fonts

#  Optional Google Fonts installation
ARG INSTALL_GOOGLE_FONTS=false
ARG GOOGLE_FONTS_SHA_COMMIT=2b5bd4077bd9269cdf3114266603372af6c3222d
ARG GOOGLE_FONTS_SHA256=e413e29c18fa727ff4d509280fd432fc0ecb1f6117eb29f2c0a87918d30fe3ad
ARG GOOGLE_FONTS_DIR="/usr/local/share/fonts/google"

ENV INSTALL_GOOGLE_FONTS=${INSTALL_GOOGLE_FONTS} \
    GOOGLE_FONTS_SHA_COMMIT=${GOOGLE_FONTS_SHA_COMMIT} \
    GOOGLE_FONTS_SHA256=${GOOGLE_FONTS_SHA256} \
    GOOGLE_FONTS_DIR=${GOOGLE_FONTS_DIR}

RUN --mount=type=cache,target=/var/cache/fonts,sharing=locked,id=google-fonts \
    bash -Eeuo pipefail -c '\
      if [[ "${INSTALL_GOOGLE_FONTS}" == "true" ]]; then \
        install-google-fonts --dest "${GOOGLE_FONTS_DIR}" --no-color && \
        fc-cache -f "${GOOGLE_FONTS_DIR}" && \
        echo "✅ Installed Google Fonts into: ${GOOGLE_FONTS_DIR}" && \
        count=$(find "${GOOGLE_FONTS_DIR}" -type f \( -iname "*.ttf" -o -iname "*.otf" -o -iname "*.ttc" -o -iname "*.otc" \) | wc -l) && \
        echo "📦 Font files found: ${count}" && \
        echo "🔎 Sample check (Roboto):" && \
        fc-list | grep -i "roboto" || true; \
      else \
        echo "📁 Skipping Google Fonts install"; \
      fi'

FROM fonts AS imagemagick

# Build-time toggles & pins
ARG INSTALL_IMAGEMAGICK=false
ARG IMAGEMAGICK_VERSION=7.1.1-47

# ✅ SHA256 for the official .tar.xz release (matches what you saw)
ARG IMAGEMAGICK_SHA256=2396cd3c4237cfbc09a89d31d1cee157ee11fbc8ec1e540530e10175cb707160

# Leave MD5 empty unless you want to pin it too
ARG IMAGEMAGICK_MD5=

# Optional explicit source URL (script has the same default internally)
ARG IMAGEMAGICK_URL="https://download.imagemagick.org/ImageMagick/download/releases/ImageMagick-${IMAGEMAGICK_VERSION}.tar.xz"

ENV INSTALL_IMAGEMAGICK="${INSTALL_IMAGEMAGICK}" \
    IMAGEMAGICK_VERSION="${IMAGEMAGICK_VERSION}" \
    IMAGEMAGICK_SHA256="${IMAGEMAGICK_SHA256}" \
    IMAGEMAGICK_MD5="${IMAGEMAGICK_MD5}" \
    IMAGEMAGICK_URL="${IMAGEMAGICK_URL}" \
    IMAGEMAGICK_PREFIX="${UNIVERSAL_TOOLBOX}/imagemagick"

# Add ImageMagick to PATH (bin symlinked too if --symlink-bin)
ENV PATH="${UNIVERSAL_TOOLBOX}/imagemagick/bin:${PATH}"

# Optional: make IM config path explicit (modules are auto-discovered)
ENV MAGICK_CONFIGURE_PATH="${IMAGEMAGICK_PREFIX}/etc/ImageMagick-7"
# (Tip: MAGICK_CODER_MODULE_PATH usually isn't needed; IM finds modules under the prefix.)

# Cache mounts: apt + sources
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=apt-cache \
    --mount=type=cache,target=/var/lib/apt,sharing=locked,id=apt-lib \
    --mount=type=cache,target=/var/cache/src,sharing=locked,id=src-cache \
    bash -Eeuo pipefail -c '\
      if [[ "${INSTALL_IMAGEMAGICK}" == "true" ]]; then \
        install-imagemagick \
          --version "${IMAGEMAGICK_VERSION}" \
          --sha256 "${IMAGEMAGICK_SHA256}" \
          ${IMAGEMAGICK_MD5:+--md5 "${IMAGEMAGICK_MD5}"} \
          --url    "${IMAGEMAGICK_URL}" \
          --prefix "${IMAGEMAGICK_PREFIX}" \
          --harden-policy --symlink-bin --no-color && \
        magick -version && \
        ldd "$(command -v magick)" | tee /tmp/ldd.magick && \
        identify -list format | egrep "PNG|JPEG|WEBP|HEIC|TIFF" | head -n 50; \
      else \
        echo "📁 Skipping ImageMagick install"; \
      fi'

# ------------------------------
# PDAL (from pinned commit)
# ------------------------------
FROM imagemagick AS pdal

# E57 (libE57Format) – optional but recommended before PDAL
ARG INSTALL_E57=false
ARG E57_REPO="https://github.com/asmaloney/libE57Format.git"

# Pin if you like: e.g. a tag or commit; leave empty for default branch
ARG E57_REF=2524923cabf0180cc559b81c13ea6c0566752a60
ARG E57_PREFIX="${UNIVERSAL_TOOLBOX}/e57"

ENV INSTALL_E57="${INSTALL_E57}" \
    E57_REPO="${E57_REPO}" \
    E57_REF="${E57_REF}" \
    E57_PREFIX="${E57_PREFIX}"

# Build E57 first so PDAL can enable the E57 plugin
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=apt-cache \
    --mount=type=cache,target=/var/lib/apt,sharing=locked,id=apt-lib \
    --mount=type=cache,target=/var/cache/src,sharing=locked,id=src-cache \
    bash -Eeuo pipefail -c '\
      if [[ "${INSTALL_E57}" == "true" ]]; then \
        install-e57format \
          --repo   "${E57_REPO}" \
          ${E57_REF:+--ref "${E57_REF}"} \
          --prefix "${E57_PREFIX}" \
          --with-deps \
          --debug && \
        test -f /etc/ld.so.conf.d/e57.conf && head -n 1 /etc/ld.so.conf.d/e57.conf || true; \
      else \
        echo "📁 Skipping E57 install"; \
      fi'

# Build-time toggles & pins
ARG INSTALL_PDAL=false

# Your commit + SHA-512 pin
ARG PDAL_COMMIT=795f0d9858dba72074fa3a4736282b1d2635620b
ARG PDAL_SHA512=2d479e7eda8f937c8f37e768c0f075d1cdad571a400659c64ad8c871f7367650825f4963ac546224d02fbd9f43ae69e9d5f822d4bae5666aae5b6d8b5e7c473e

# Optional alternatives (leave empty to use commit pin)
ARG PDAL_VERSION=
ARG PDAL_URL=

ENV INSTALL_PDAL="${INSTALL_PDAL}" \
    PDAL_COMMIT="${PDAL_COMMIT}" \
    PDAL_SHA512="${PDAL_SHA512}" \
    PDAL_VERSION="${PDAL_VERSION}" \
    PDAL_URL="${PDAL_URL}" \
    PDAL_PREFIX="${UNIVERSAL_TOOLBOX}/pdal"

# Put PDAL on PATH once installed (script also registers libs via ld.so.conf.d)
ENV PATH="${PDAL_PREFIX}/bin:${PATH}"

# Cache mounts: apt + sources
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=apt-cache \
    --mount=type=cache,target=/var/lib/apt,sharing=locked,id=apt-lib \
    --mount=type=cache,target=/var/cache/src,sharing=locked,id=src-cache \
    bash -Eeuo pipefail -c '\
      if [[ "${INSTALL_PDAL}" == "true" ]]; then \
        set -x; \
        install-pdal \
          --commit "${PDAL_COMMIT}" \
          ${PDAL_VERSION:+--version "${PDAL_VERSION}"} \
          ${PDAL_URL:+--url "${PDAL_URL}"} \
          --sha512 "${PDAL_SHA512}" \
          --prefix "${PDAL_PREFIX}" \
          --with-deps \
          --symlink-bin \
          --debug && \
        pdal --version && \
        pdal --drivers | head -n 50 && \
        gdalinfo --version && \
        test -f /etc/ld.so.conf.d/pdal.conf && head -n 1 /etc/ld.so.conf.d/pdal.conf; \
      else \
        echo "📁 Skipping PDAL install"; \
      fi'


# FROM environment AS texlive

# # Optional TeX Live installation
# ARG INSTALL_TEXLIVE=false

# # Set texlive directories.
# ENV TEXLIVE_INSTALL_PREFIX="${XDG_DATA_HOME}/texlive"
# ENV TEXMFHOME="${TEXLIVE_INSTALL_PREFIX}/texmf"
# ENV TEXMFVAR="${TEXLIVE_INSTALL_PREFIX}/.texlive/texmf-var"
# ENV TEXMFCONFIG="${TEXLIVE_INSTALL_PREFIX}/.texlive/texmf-config"
# ENV INSTALL_TEXLIVE=${INSTALL_TEXLIVE}

# # Optional TeX Live installation
# RUN if [ "${INSTALL_TEXLIVE}" = "true" ]; then \
#     apt-get install --yes --no-install-recommends texlive-full=2023.20240207-1; \
#     else \
#     echo "📁 Skipping texlive-full install"; \
#     fi

# FROM base AS dependencies

# # Disable the automatic removal of downloaded packages
# RUN rm -f /etc/apt/apt.conf.d/docker-clean

# # Fix for update-alternatives: error:
# # 'error creating symbolic link '/usr/share/man/man1/rmid.1.gz.dpkg-tmp': No such file or directory'
# # See https://github.com/debuerreotype/docker-debian-artifacts/issues/24#issuecomment-360870939
# RUN mkdir --parents /usr/share/man/man1



# # COPY --from=fonts /opt/devtools/fonts /opt/devtools/fonts
# RUN fc-cache -f -v

# # Configure the system locale and timezone
# RUN echo "LC_ALL=en_US.UTF-8" >> /etc/environment \
#     && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
#     && echo "LANG=en_US.UTF-8" > /etc/locale.conf \
#     && locale-gen en_US.UTF-8 \
#     && update-locale LANG=en_US.UTF-8 \
#     && dpkg-reconfigure locales



# # Copy .tool-versions file
# COPY .tool-versions ${WORKSPACE_HOME}/.tool-versions

# # Install asdf version manager and plugins along with taskfile
# RUN /usr/bin/env bash ${UNIVERSAL_BIN}/setup-asdf

# FROM devtools AS final

# # Ensure SYS_UID_MAX and SYS_GID_MAX are set to high values, uncommented or inserted
# RUN /usr/bin/env bash ${UNIVERSAL_BIN}/set-sys-uid-max

# # Create the directory in advance so ownership can be adjusted later
# RUN mkdir -p "${UNIVERSAL_HOME}"

# # Copy and source custom shell aliases
# COPY shell/aliases /etc/profile.d/aliases.sh

# # Ensure correct permissions and sourcing
# RUN chmod 644 /etc/profile.d/aliases.sh && \
#     echo '[ -d /etc/profile.d ] && for f in /etc/profile.d/*.sh; do [ -r "$f" ] && . "$f"; done' \
#     >> /etc/bash.bashrc

# RUN echo 'source /etc/profile.d/aliases.sh' >> /etc/zsh/zshrc

# ------------------------------
# shdoc (Bash doc generator)
# ------------------------------
FROM pdal AS shdoc

# Build-time toggles & pins
ARG INSTALL_SHDOC=false
ARG SHDOC_REPO="https://github.com/reconquest/shdoc.git"

# Optional git ref (tag/branch/commit). Leave empty for default branch.
ARG SHDOC_REF=""

# Install prefix (script defaults to /usr/local if omitted)
ARG SHDOC_PREFIX="${UNIVERSAL_TOOLBOX}/shdoc"

ENV INSTALL_SHDOC="${INSTALL_SHDOC}" \
    SHDOC_REPO="${SHDOC_REPO}" \
    SHDOC_REF="${SHDOC_REF}" \
    SHDOC_PREFIX="${SHDOC_PREFIX}"

# Ensure the chosen prefix bin is on PATH (covers non-/usr/local installs)
ENV PATH="${SHDOC_PREFIX}/bin:${PATH}"

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=apt-cache \
    --mount=type=cache,target=/var/lib/apt,sharing=locked,id=apt-lib \
    bash -Eeuo pipefail -c '\
      if [[ "${INSTALL_SHDOC}" == "true" ]]; then \
        install-shdoc \
          --repo   "${SHDOC_REPO}" \
          ${SHDOC_REF:+--ref "${SHDOC_REF}"} \
          --prefix "${SHDOC_PREFIX}" \
          --with-deps \
          --symlink-bin \
          --debug && \
        which shdoc && shdoc -h >/dev/null 2>&1 || shdoc --help >/dev/null 2>&1 && \
        echo "✅ shdoc installed to ${SHDOC_PREFIX}"; \
      else \
        echo "📁 Skipping shdoc install"; \
      fi'


# FROM gcloud AS final
FROM cpython AS final

# Make tini the entrypoint; pass-through args with "--"
ENTRYPOINT ["/usr/bin/tini","--"]

# Leave CMD light; devcontainers will override as needed
CMD ["bash", "-lc", "sleep infinity"]
