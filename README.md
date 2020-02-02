[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Assumptions

 * You're comfortable editing (or learning to work with) Markdown
 * You're able to create your content as a Gihub wiki
 * You have a Github user
 * You optionally have a Github organisation
 * You have a repository for your user or organisation, which can be <user|organisation.github.io> if you're creating a user/organisation site (See https://help.github.com/en/articles/about-github-pages#types-of-github-pages-sites for details)
 * Your repository is public (specifically, it can be accessed by someone not logged in to Github, and cloned using an https url)
 * You're able to generate a user token for your Github account with ? privileges (or create an account with access to just this repo)

## Wikload

Upload files to a Github wiki using Govuk frontend.

If you want to password-protect the upload app you can set the environment variables `USERNAME` and `PASSWORD` in the Heroku config vars section.

### Usage

Deploy this app to Heroku and set the environment variable `GITHUB_REPO`.

If you want password protection, add `USERNAME` and `PASSWORD` config variables to your Heroku app.

Browse to your Heroku app url to confirm that it's working as expected.

### Contributing

Forks and pull requests welcome.

David
