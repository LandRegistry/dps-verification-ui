# Verification UI Information

This repository contains a flask application that provides access for member of the Data Services Team to investigate applications to download data that have come through the Get Land and Property Data service.

It constitutes a worklist where pending applications can be viewed, selecting one of these applications will take the user to a screen where they can view the applications details and choose to add notes to record information about their investigations into the application. Then the user can either accept or decline an application.

## Routes

### `/worklist`

Retrieves details of all pending applications from verification-api and extracts certain information such as id, date, name and user type to format into a list to display in the template.

### `/worklist/<item_id>`

Retrieves the details of a specific pending application from verification-api based on the item_id that is passed through. Then extracts and formats some of the information into a list of details to displayed on the template. Also extracts details of any notes returned from verification-api to display in a 'notepad' section on the template. Finally instantiates any forms for actions such as declining to render on the template, and locks the application to the user if a lock wasn't already in place.

### `/approve`

Passes the id of the application and the staff id of the user that approves the application through to verification-api to approve the appllication in the backend. If successful it then redirects the user back to the worklist displaying a message that the application was approved.

### `/decline`

Passes the id of the application, the staff id of the user that declines the application and the decline reason that they entered/selected through to verification-api to decline the appllication in the backend. If successful it then redirects the user back to the worklist displaying a message that the application was declined.

### `/note`

Passes the id of the application, the staff id of the user that adds the note and the text they entered through to verification-api which will add the note onto the application data on the backend. If successful it then redirects the user back to the application details screen displaying a message that the note was added.

### `/close`

Passes the id of the approved application (user account), the staff ID of the user that performs the closure, the requester (user or HMLR) and the closure reason through to the verification-api, which then performs the closure by removing the account from LDAP and CKAN's database while keeping it in DST's database for record-keeping purposes.

### `/lock`

Transfers a pending application's lock to the requesting user so that they can perform actions.

### `/unlock`

Removes a pending application's lock so that any other DST user can perform actions.

### `/search`

Performs a search of all applications and accounts based on parameters supplied by the user.

### `/update_dataset_access`

Take the form data from the data access form (a checkbox list of restricted datasets) and submits the full list and which datasets have been checked to verification_api so that the appropriate membership for the application can be added or removed on ldap.


## Asset Related Information

### CSS

The GOV.UK design system only comes with a single flavour of button and so as there were to be more than one button on the worklist details screen I added styles for red and blue button into partials/buttons.scss

Also added custom style for the notepad component of the worklist details page as there was no existing component for such a function in the GOV.UK design system. The component is basically a scrollable box with notes listed seperated by a bottom border.

### Javascript

The common decline reasons drop down contain a list of common decline reasons retrieved from a table in the backend when the user selects a common decline reason an clicks on the Add button the decline reason text is populated with the text for the commond decline reason selected. This is only available for user with javscript however. I have wrapped those from elements in a `js-only` style so that users without javascript won't see them but will still be able to enter a decline reason using the text area.

# General Flask Skeleton Information

This application was built from [flask-skeleton-ui](http://gitlab.service.dev.ctp.local/skeletons/flask-skeleton-ui) the sections below are more general information relating to this and how to work with it.

## Quick start

### Docker

This app supports the [universal dev-env](http://gitlab.service.dev.ctp.local/common/dev-env) so adding the following to your dev-env config file is enough:

```YAML
  verification-ui:
    repo: git@gitlab.service.dev.ctp.local:skeletons/verification-ui.git
    branch: master
```

The Docker image it creates (and runs) will install all necessary requirements and set all environment variables for you.

### Standalone

#### Environment variables to set

* PYTHONUNBUFFERED *(suggested value: yes)*
* PORT
* LOG_LEVEL
* COMMIT
* APP_NAME

##### When not using gunicorn

* FLASK_APP *(suggested value: verification_ui/main.py)*
* FLASK_DEBUG *(suggested value: 1)*

#### Running (when not using gunicorn)

(The third party libraries are defined in requirements.txt and can be installed using pip)

```shell
python3 -m flask run
or
flask run
or
make run
```

## Testing

### Unit tests

The unit tests are contained in the unit_tests folder. [Pytest](http://docs.pytest.org/en/latest/) is used for unit testing. To run the tests use the following command:

```bash
make unittest
(or just py.test)
```

To run them and output a coverage report and a junit xml file run:

```bash
make report="true" unittest
```

These files get added to a test-output folder. The test-output folder is created if doesn't exist.

You can run these commands in the app's running container via `docker-compose exec verification-ui <command>` or `exec verification-ui <command>`. There is also an alias: `unit-test verification-ui` and `unit-test verification-ui -r` will run tests and generate reports respectively.

### Integration tests

The integration tests are contained in the integration_tests folder. [Pytest](http://docs.pytest.org/en/latest/) is used for integration testing. To run the tests and output a junit xml use the following command:

```shell
make integrationtest
(or py.test integration_tests)
```

This file gets added to the test-output folder. The test-output folder is created if doesn't exist.

To run the integration tests if you are using the common dev-env you can run `docker-compose exec verification-ui make integrationtest` or, using the alias, `integration-test verification-ui`.

## Application Framework implementation

Although you should inspect every file and understand how the app is put together, here is a high level list of how the [Application Framework](http://techdocs.dev.ctp.local/index.php/Application_Framework) standard structure and behaviours are implemented:

### Universal Development Environment support

Provided via `configuration.yml`, `Dockerfile` and `fragments/docker-compose-fragment.yml`.

`configuration.yml` lists the commodities the dev env needs to spin up e.g. postgres. The ELK stack is spun up when "logging" is present.

The `docker-compose-fragment.yml` contains the service definiton, including the external port to map to, sharing the app source folder so the files don't need to be baked into the image, and redirection of the stdout logs to logstash via syslog.

The `Dockerfile` simply sets the APP_NAME environment variable and installs the third party library requirements. Any further app-specific variables or commands can be added here.

### Logging in a consistent format (JSON) with consistent content

Flask-LogConfig is used as the logging implementation. It is registered in a custom extension called `enhanced_logging`. There is also a filter that adds the current trace id into each log record from g, and a formatter that puts the log message into a standard JSON format. The message can then be correctly interpreted by both the dev-env and webops ELK stacks. The configuration that tells Python logging to use those formatters and the filter is also set up in `enhanced_logging`.

### Consistent way to run the application

`main.py` imports from `app.py` in order to trigger the setup of the app and it's extensions. It also provides the app object to `manage.py`.

`manage.py` contains the app object which is what should be given to a WSGI container such as gunicorn. It is also where Alembic database migration code is to be placed.

All Flask extensions (enhanced logging, SQLAlchemy, socketIO etc) shoud be registered in `extensions.py`. First they are created empty, then introduced to the app in the `register_extensions()` method (which is then called by `main.py` during initialisation).

### A Makefile with specific commands to run unit tests and integrations tests

`Makefile` - This provides generic language-independent functions to run unit and integration tests  (useful for the build pipeline).

### Consistent Unit test and integration test file structure

Provided via `unit_test` and `integration_test` directories. These locations do not have an `__init__.py` so the tests cannot be accidentally imported into other areas of the app. This links in with the management script as it expects the tests to be in these locations. The file `setup.cfg` also contains the default test entry point and coverage settings.

### An X-API-Version HTTP header returned in all responses detailing the semantic version of the interface

Not applicable

### An X-Trace-ID HTTP header received/generated and then propagated

Provided by the `before_request()` method in `main.py` in the enhanced_logging custom extension. If a header of that name is passed in, it extracts it and places it into g for logging (see next section) and also creates a requests Session object with it preset as a header. This allows the same value to propagate throughout the lifetime of a request regardless of how many UIs/APIs it passes through - making debugging and tracing of log messages much easier.

Note that for the propagation to work, g.requests must be used for making calls to other APIs rather than just requests.

### Consistent error response structure (but not content)

In `exceptions.py` there is a custom exception class ApplicationError defined, which can be raised by applications that need to send back details of an error to the client. There is a handler method defined that converts it into a consistent response, with JSON fields and the requested http status code.

There is also a handler method for any other types of exception that manage to escape the route methods. These are always http code 500.

Both handlers are registered in the `register_exception_handlers()` method, which is called by main.py in a similar way to registering  blueprints.

### Consistent environment variable names

All config variables the app uses are created in `config.py`. It is a plain python module (not a dict or object) and no region-specific code. The mandatory variables are `FLASK_LOG_LEVEL` (read by Flask automatically), `COMMIT` and `APP_NAME` (both used in the health route).

This should be the only place environment variables are read from the underlying OS. It is effectively the gateway into the app for them.

### Consistent implementation of health and cascading health endpoints

Routes are logically segregated into separate files within `/views`. By default a `general.py` is provided that creates the health routes (see table above) that returns a standardised set of JSON fields. Note how the app name is retrieved using the APP_NAME config variable (which in turn comes from the environment).

Blueprints are registered in the `register_blueprints` method in `blueprints.py` (which is then called by `main.py` during initialisation).

### Concise and clear requirements management

The only (non-test related) requirements that should be changed by hand are those in `requirements.in`. They are the top -level requirements that are directly used by the application. When one of these is updated, the tool `pip-compile` should be used to generate a full requirements.txt that contains all sub-dependencies, pinned to whatever version is available at the time. Both files should be in source control. See [TechDocs](http://techdocs.dev.ctp.local/index.php/Requirements_management) for further explanation.


## Other useful documentation

### Building frontend assets (CSS, JS etc)

See [verification_ui/assets](verification_ui/assets) for more details.

At a high level this includes:
- Sass - because writing raw CSS is painful.
- Webpack - for bundling JavaScript modules. To help us write modular, maintainable code and avoid "JavaScript spaghetti".
- Babel - to let us use modern syntax which makes JavaScript nicer to write and in some cases reduce code complexity.

### GOV.UK template

The GOV.UK template is pulled in automatically from the npm package that gets installed. This happens on every build, so while the file is committed into the repository, you should not modify it manually yourself.

If you need to customise the file, make a copy of it and change your other templates to extend your copy instead of the original. When the GOV.UK kit gets updated, you then have a reference to use when bringing the updates in.

### Removing the GOV.UK frontend code

If you want to remove the GOV.UK frontend code in order to do something else such as Bootstrap or just custom stuff, you will need to make the following changes:

- Remove the reference to `land-registry-elements` from the `sassIncludePaths` array in `Gulpfile.js`
- Remove references to GOV.UK from `verification_ui/.gitignore`
- Remove `govuk_elements_jinja_macros` and `land_registry_elements` from the template `PrefixLoader` in `verification_ui/app.py`
- Remove any references to GOV.UK from your app's SCSS and JS files
- Change `verification_ui/custom_extensions/jinja_markdown_filter/main.py` to use `misaka.HtmlRenderer` instead of the custom `GovRenderer` and update the unit tests to suit.
- Remove the references to GOV.UK from `verification_ui/templates/layout.html` and implement your own base layout template.
- Remove `govuk-frontend` and `land-registry-elements` from `package.json` and regenerate your `package-lock.json`
- Remove `govuk-elements-jinja-macros` and `land-registry-elements` dependencies from `pipcompilewrapper.sh`
- Tweak the Content-Security-Policy to suit your new needs

### Using the GOV.UK toolkit on a non service.gov.uk domain

The GOV.UK toolkit can be used freely to build anything you like, however there are restrictions on the use of the Crown and the Transport font which can only be used on the following URLs:

- gov.uk/myservice
- myservice.service.gov.uk
- myblog.blog.gov.uk

_(Taken from https://www.gov.uk/service-manual/design/making-your-service-look-like-govuk)_

In order to use the toolkit elsewhere you therefore need to stop using these. This can be done as follows:

- Make your own copy of the govuk template (Don't edit the one that's already there - this one will be overwritten when updating the GOV kit)
- Find code that looks like the following blocks and delete them:

  ```
  <link rel="shortcut icon" href="{{ assetPath | default('/assets') }}/images/favicon.ico" type="image/x-icon" />
  <link rel="mask-icon" href="{{ assetPath | default('/assets') }}/images/govuk-mask-icon.svg" color="{{ themeColor | default('#0b0c0c') }}"> {# Hardcoded value of $govuk-black #}
  <link rel="apple-touch-icon" sizes="180x180" href="{{ assetPath | default('/assets') }}/images/govuk-apple-touch-icon-180x180.png">
  <link rel="apple-touch-icon" sizes="167x167" href="{{ assetPath | default('/assets') }}/images/govuk-apple-touch-icon-167x167.png">
  <link rel="apple-touch-icon" sizes="152x152" href="{{ assetPath | default('/assets') }}/images/govuk-apple-touch-icon-152x152.png">
  <link rel="apple-touch-icon" href="{{ assetPath | default('/assets') }}/images/govuk-apple-touch-icon.png">
  ```

  ```
  <meta property="og:image" content="{{ assetUrl | default('/assets') }}/images/govuk-opengraph-image.png">
  ```


- Create a new favicon for your app in `verification_ui/assets/src/images` and re-point the shortcut icon to point to it as follows:

  ```
  <link rel="shortcut icon" href="{{ url_for('static', filename='images/app/favicon.ico') }}" type="image/x-icon" />
  ```

- Replace the call to `govukHeader` to be your own custom code as appropriate
- Add the following code to the top of your `main.scss` file, above the `govuk-elements` import:

  ```
  $govuk-font-family: "Comic Sans MS", cursive, sans-serif
  ```
- Rebuild your CSS by running `npm run build`

### Support for Flask `flash()` messages

Messages registered with the Flask `flash()` method will appear at the top of the page in a styled box.
`flash('Something something', 'error')` will raise a message using the error style, whereas `flash('Message')` will produce a more neutral looking "information" style message.

#### GOV.UK Jinja macros

The GOV.UK design system includes a range of macros for generating their markup. Using these is beneficial because your markup will always keep in step with the version of the kit you are using. These macros are ported to Jinja from their Nunjucks equivalents automatically by the nodejs build process.

The GOV.UK macros can be imported into your template as follows:

```
{% from "app/vendor/.govuk-frontend/components/phase-banner/macro.html" import govukPhaseBanner %}
```

and then used:

```
  {{ govukPhaseBanner({
    'tag': {
      'text': "alpha"
    },
    'html': 'This is a new service – your <a class="govuk-link" href="#">feedback</a> will help us to improve it.'
  }) }}
```

This is the broadly same as is documented in the GOV.UK design system so you can follow their guidelines on the whole. For example, the phase banner documentation can be found at https://design-system.service.gov.uk/components/phase-banner/

There are important differences to bear in mind though, as follows:

- When invoking macros with a dict as above, remember that keys should be quoted. Because the GOV.UK design system is written for Nunjucks/Node.JS they do not quote their keys and so copying and pasting their code examples directly will not work.
- Import paths for the macros are different to those in the documentation. Note how in the above for example the macro is pulled from `app/vendor/.govuk-frontend/components` and the file extension is `.html` instead of `.njk`

### Flask-WTForms

[Flask-WTForms](https://flask-wtf.readthedocs.io/en/stable/) is included and should be used for all forms.

This has been extended by the use of custom widgets which make it extremely easy to generate GOV.UK style forms. See [verification_ui/custom_extensions/wtforms_helpers](verification_ui/custom_extensions/wtforms_helpers) for detailed usage instructions.

#### CSRF protection

Forms are protected with the CSRF protection built in to Flask-WTF. This is customised to handle the CSRFError exception that gets thrown and show users a message when it occurs. It is worth considering however whether you should warn users of this upfront, before they start filling out a form. Otherwise there is a risk their session will time out after an hour and their form submission will be thrown away, forcing them to do it again.

If you need to exempt a view from CSRF, you need to import the csrf instance from the csrf extension as follows:

```
from verification_ui.custom_extensions.csrf.main import csrf

@csrf.exempt
@my_blueprint.route("/")
def index_page():
    ...
```

### ApplicationError templates
The ApplicationError class contains a code parameter when raising exceptions, such as:

```
raise ApplicationError('Friendly message here', 'E102', 400)
```

If this exception goes uncaught in your code, it will bubble up to the application  error handler. At this point, it will try to find a template named `E102.html` in the `verification-ui/templates/errors/application` folder to allow you to write custom error pages on a per error code basis.

If it cannot find this template, it will fall back to `application.html` and show a generic message.

Do not feel you have to make custom templates for every error code. This is an _optional feature_, not a requirement.

### Markdown

`verification_ui/custom_extensions/jinja_markdown_filter` exposes a jinja template filter which can be used to render markdown to GOV.UK compatible html. It's well suited to things like Terms and conditions pages which could be written in markdown and rendered to HTML on the fly.

```
  {{ my_variable_containing_some_markdown_content|markdown }}
```

or

```
{% filter markdown %}
  # This is markdown

  - Hello
  - World
{% endfilter %}
```

### Content Security Policy

The Content-Security-Policy (CSP) HTTP response header helps you reduce Cross Site Scripting (XSS) risks on modern browsers by declaring what dynamic resources are allowed to load via a HTTP Header. This has been configured with some sensible defaults that will work out the box for a GOV.UK frontend.

#### Modes

There are two modes available. `full` and `report-only`. These are configured via the `CONTENT_SECURITY_POLICY_MODE` environment variable. It is recommended that you initially use `report-only` which will test but not enforce the rules and monitor the logs for violations. If none are found after a bedding in period, it should be switched to `full` at which point the security protections will begin to be enforced.

#### Gotcha #1: How to write inline scripts

One of the main features of CSP is that it blocks inline script tags. This is a robust protection against XSS but it does sometimes get in the way of simple Google Analytics implementations and other uses of inline scripts. The best answer to this is _not to write inline scripts_. If you do everything in actual .js files you will not fall foul of the CSP.

The difficulty this may present is that sometimes it is necessary to pass data from the backend through to the frontend. This is commonly done by writing values from the Python app directly into JavaScript variables. Unfortunately this is exactly the thing that CSP is trying to prevent, since these values will often be user generated either directly or indirectly. A specially crafted value might "break out" of the variable declaration and inject malicious JS into the page (In a very similar manner to SQL injection).

There are a few options which can be used to work around this:

##### `data-` attributes

Simple bits of data could be included as follows:

```html
<div data-lat="50" data-lng="-4" id="my-map"></div>
```

This can then be accessed in jQuery:

```js
var $map = $('#my-map')
var lat = $map.data('lat')
var lat = $map.data('lng')
```

This is only really suitable for fairly simple pieces of data and it requires you to place it on a related HTML element. Data should not be arbitrarily placed on unrelated HTML elements purely for the sake of passing it around. In the above example, lat and lng are used to center the map once it is initialised, hence the data is related to the component on which it is stored.

##### JSON in script tags

For data beyond just simple strings, or data that isn't obviously associated with a component, you can stick JSON in script tags as follows:

```
<script type="application/json" id="my-data">
  {
    "center": {
      "lat": "50",
      "lng": "-4"
    },
    "polygon": [1, 2, 3, 4, 5, 6, 7, 8, 9 ...]
  }
</script>
```

This can then be loaded into your JavaScript files like this:

```js
var configElement = document.getElementById('my-data')
rules = JSON.parse(configElement.innerHTML)
```

##### Hidden form fields

Data can also be rendered into hidden form fields:

```html
<input type="hidden" name="lat" value="50" id="lat">
<input type="hidden" name="lng" value="-4" id="lng">
```

And then accessed like:

```js
var lat = document.getElementById('lat').value
var lng = document.getElementById('lng').value
```

#### Gotcha #2: Referencing scripts via CDN

Another feature of CSPs is that they block external JavaScript and CSS loading from domains that are not in the approved list. If you need to add a new external stylesheet, you will need to add the domain to the `script-src` or `style-src` declarations in the CSP in verification_ui/custom_extensions/content_security_policy/main.py.

When doing this however **it is vital that you include a Sub Resource Integrity (SRI) hash on the script tag**. See https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity for details on how to do this. This is essential in order to mitigate against the possibility of malicious code being injected if the CDN were compromised, or someone managed to achieve a man in the middle attack. When SRI is used, the browser will not run the script if the contents do not match the hash.

Future iterations of the CSP will strictly enforce SRI, but this is not currently in place due to poor browser support.

#### Useful further reading

https://content-security-policy.com/
https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
https://www.owasp.org/index.php/Content_Security_Policy_Cheat_Sheet


### ADFS authentication
If you are looking to use ADFS for authenticating users, see this section on techdocs:

[OAuth2 for Internal Users via ADFS - Implementation Guide](http://techdocs.dev.ctp.local/index.php/OAuth2_for_Internal_Users_via_ADFS_-_Implementation_Guide)
