# Changelog

All notable changes to this project will be documented in this file.

<!-- marker -->
## [v2.0.0](https://github.com/dtomlinson91/easy-email-downloader/commits/v2.0.0) - 2022-05-24
<small>[Compare with v1.0.2](https://github.com/dtomlinson91/easy-email-downloader/compare/v1.0.2...v2.0.0)</small>

### ✨ Features

- 💥 **breaking**: Add filename to downloaded attachments ([c4a4556](https://github.com/dtomlinson91/easy-email-downloader/commit/c4a4556a2acc066c02980a80ba4b91ecb465709c))

The way attachments are accessed has changed.

`Email.attachments` now contains a list of `Attachment` objects instead of a list of bytes.

Available attributes on an `Attachment` object are `Attachment.filename` and `Attachment.contents`
### 🎨 Styling

- Run black & isort ([65db7d3](https://github.com/dtomlinson91/easy-email-downloader/commit/65db7d3522338d6ffee9a8da914e00a62c7e3131))
### 🐛 Bug Fixes

- Fix bug where returned mailbox is `None` ([a1f69eb](https://github.com/dtomlinson91/easy-email-downloader/commit/a1f69eb9a0e2d634b1b93aaf39533ecb50dff4fd))
### 📘 Documentation

- Add `setup.py` instructions to README ([1849768](https://github.com/dtomlinson91/easy-email-downloader/commit/18497684e45143a38d1133e2d27848e7d7fee6f5))
- Update README with use cases and todo list ([6c02e8b](https://github.com/dtomlinson91/easy-email-downloader/commit/6c02e8ba34455644bdc6e9bd64f1e7ff9e68e8ca))
- Update example to make clear `EmailFilter` is optional ([2bc6738](https://github.com/dtomlinson91/easy-email-downloader/commit/2bc6738af4a7b083bb5f21f653dbc97407a87d91))
### 🛠 Refactor/Improvement

- Move `__version__.py` to `_version.py` ([fcd7215](https://github.com/dtomlinson91/easy-email-downloader/commit/fcd721509e3f98d8a898ab858a12cac8caff2ee0))
- Refactor code base into own modules ([82cbdda](https://github.com/dtomlinson91/easy-email-downloader/commit/82cbddaa57723ce5363b6261a78692f05a00d01b))
## [v1.0.2](https://github.com/dtomlinson91/easy-email-downloader/commits/v1.0.2) - 2022-04-24
<small>[Compare with v1.0.1](https://github.com/dtomlinson91/easy-email-downloader/compare/v1.0.1...v1.0.2)</small>

### 🥱 Miscellaneous Tasks

- Fix wrong links in `CHANGELOG.md` ([f30ad18](https://github.com/dtomlinson91/easy-email-downloader/commit/f30ad181f7de8a8fc2cf5d283488121aa88f58d6))
- Remove old `_version.py` ([c6c4698](https://github.com/dtomlinson91/easy-email-downloader/commit/c6c469810430630f2a59fa84c914b94a8f720f06))
- Remove `.DS_STORE` ([e551bab](https://github.com/dtomlinson91/easy-email-downloader/commit/e551bab3a6bd4a0f8f2466496bb56bea19ece95d))
- Remove sensitive example `playground.py` ([8e8784d](https://github.com/dtomlinson91/easy-email-downloader/commit/8e8784d9574bab21052c7ecc3be7d6fbf5662a57))
## [v1.0.1](https://github.com/dtomlinson91/easy-email-downloader/commits/v1.0.1) - 2022-04-24
<small>[Compare with v1.0.0](https://github.com/dtomlinson91/easy-email-downloader/compare/v1.0.0...v1.0.1)</small>

### 🥱 Miscellaneous Tasks

- Update metadata for PyPI homepage ([df0bc59](https://github.com/dtomlinson91/easy-email-downloader/commit/df0bc597d2a79ee829ac490867ec15a177daff63))
## [v1.0.0](https://github.com/dtomlinson91/easy-email-downloader/commits/v1.0.0) - 2022-04-24

### ✨ Features

- Initial release v1.0.0 ([eb2cfd4](https://github.com/dtomlinson91/easy-email-downloader/commit/eb2cfd4700f8b432c67367cbe41286061ab5a1ec))
