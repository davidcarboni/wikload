## Todo

Need to commit images to the wiki repo, rather than the main repo.

## Assumptions

 * You're comfortable editing (or learning to work with) Markdown
 * You're able to create your website content as a Gihub wiki
 * You have a Github user
 * You optionally have a Github organisation
 * You have a repository for your user or organisation, which can be <user|organisation.github.io> if you're creating a user/organisation site (See https://help.github.com/en/articles/about-github-pages#types-of-github-pages-sites for details)
 * Your repository is public (specifically, it can be accessed by someone not logged in to Github, and cloned using an https url)
 * You're able to generate a user token for your Github account with ? privileges (or create an account with access to just this repo)

## Govwiki

Render a Github wiki using Govuk frontend.

The files in this repository can be copied into a Github wiki repo (https://github.com/username/repo[.wiki].git) and the result pushed to Heroku to create a Govuk-styled rendering of the wiki content.

If you need to password-protect the content (for example if you're not currently working in the open) you can set the environment variables `USERNAME` and `PASSWORD` in the Heroku config vars section.

### Usage

Check out your wiki repo, which will be `https://github.com/user/repo.wiki.git` - NB it's `.wiki.git` for the wiki, distinct from the main repo, which is just `.git`.

If you want password protection, add `USERNAME` and `PASSWORD` config variables to your Heroku app.

Copy the files from this repo into your wiki repo and check them in (you can skip `README.md`, `Dockerfile` and `run.sh`). Follow the instructions for adding a Heroku remote (Heroku will give you these instructions when you create a new app, on the Deployment tab). Push to Heroku with a `git push heroku master`.

Browse to your Heroku app url to confirm that it's working as expected.

### Contributing

Forks and pull requests welcome.

David
