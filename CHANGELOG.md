# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and as of version 3.0.0 this project adheres to [Semantic Versioning](http://semver.org/).

## [1.15.1]

### Added

- added pycrypto library and altered library versions

## [1.15.0]

### Updated

- Python 3.6 upgrade

## [1.14.0]

### Added

- Ability to go back to search from worklist items without form re-submission
- Ability to add 'next steps' when declining an application to update service email content

### Fixed

- 'Add text' functionality in IE browsers
- Jump to top of page when adding note to account

## [1.13.0]

### Added

- New page to allow DST to update individual contact preferences for user
- Removed audit points for approving and declining applications
- Removed audit points for modifying a user's dataset access permissions
- Removed audit points for changing a user's contact preferences
- Added new audit points for staff user login
- Added trace_id for audit points

## [1.12.1]

### Fixed

- Refactored GovIterableBase to allow for attributes to be included for each field
- Updated close_requester to include attribute 'required' in parameters
- Issue with not being able to update contact prefs due to locked accounts

## [1.12.0]

### Fixed

- Changed wording of no download message in download history to avoid confusion when no date present

### Added

- Audit events for successful/unsuccessful DST sign in

## [1.11.0]

### Added

- New section in account_details template for datasdet activity and function to build data object and html string to display the activity in the template
- Refactor search functionality:
- only store search parameters in flask session which reduces header size and fixes nginx proxy buffer issues
- limit number of search results returned and notify user that limit has been exceeded

## [1.10.1]

### Fixed

- Fixed HTML validation errors that were flagged by the accessibility audit

## [1.10.0]

### Changed

- Amended the data access form to be constructed using a single call to verification-api to get all relevant data about private datasets in the service and what the user currently has access to.
- Rendering two different templates for application and account based on the status of the item that is being requested from worklist/search.

## [1.9.1]

### Fixed

- Fixed the error where a DST user trying to approve, delete or update an account when they are still in the application but the lock has been taken by another user. The DST user will now be redirected back to the worklist page instead.

## [1.9.0]

### Added

- New action of 'Data access' available when account is in Approved status where user can select from list of restricted datasets which to grant or remove access for the account.

### Changed

- Actions 'Data access' and 'Close account' now displayed as tabs in the account details page.

## [1.8.0]

### Added

- Ability for DST to update a user's contact preferences:
    - New form on worklist item to post preferences
    - Update item with new note detailing the change

## [1.7.3]

### Changed

- Format address function now handles overseas organisation country key error

## [1.7.2]

### Added

- Add appropriate message if email was sent to user after account closure 

## [1.7.1]

### Changed

- Updated Verification API URLs for new API version
- Updated references to API response attributes for new API version

## [1.7.0]

### Fixed

- Attempting to access an unknown case ID now gives a HTTP 404 instead of a HTTP 500
- Country now only shows for non-UK accounts
- Postcode is displayed before Country, instead of after

### Changed

- Viewing item details from Worklist now clears search results, to avoid locking information in search results becoming outdated
- Fewer calls to Verification API due to refactor - now calls are only made when necessary

## [1.6.2]

### Fixed

- Missing 'Status' column header

## [1.6.1]

### Fixed

- Missing 'Account Type' column

## [1.6.0]

### Added

- Tabs for separated views for applications and search functionality


## [1.5.0]

### Added

- Additional column in worklist for viewing lock status of cases
- Banner at the top of worklist item page to represent and allow change to lock status of cases

### Changed

- Removed account type from worklist to make some room for new columns, as context presents fixed value
- Users can now only Approve, Decline and add comments while a case is locked to them

## [1.4.0]

### Added

- Added ability to close service user accounts via details page

### Changed

- Places application actions behind a dynamic radio button, make the UI clearer for users
## [1.3.0]

### Added

- Added In Progress status to worklist items

## [1.2.1]

### Changed

- Fixed linting issues where variable not used and url_for wasn't imported in login.py

## [1.2.0]

### Added

- Enable role based access for ADFS Login

## [1.1.0]

### Added

- Allow us to bypass ADFS in test environment for testing

## [1.0.0]

### Added

- The very first release for private beta 
