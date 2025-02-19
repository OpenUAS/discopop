---
layout: default
title: How to contribute
nav_order: 8
---

# Contributing
## Reporting a bug or requesting a feature
If you have encountered a bug or would like to request or propose a new feature, please feel free to create a new issue using the appropriate template.

## Implementing a requested feature or fixing a known bug
If you want to fix a known bug or implement a new feature, please first create a fork of the repository.
After you have implemented your changes, you can propose them for inclusion in the project by creating a pull request from your fork into the `master` branch.
Please link the issue of the implemented feature or the fixed bug in the pull request for clearness, or add the respective [keywords](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword#linking-a-pull-request-to-an-issue-using-a-keyword).

# Contributing as a project member
## Reporting a bug or requesting a feature
The process is identical to the previously mentioned process for contributors which are not part of the project.

## Solving an issue
The process to solve an already known issue (bug or feature request) is basically identical to the previously described process.
However, instead of creating a fork of the repository please create a branch with a descriptive name, which allows to understand it's purpose and it's relation to the targeted issue.
A good and easy option for this is to use the `Create a branch` link which can be found in the `Development` section of each issue.
Follow the instructions for determining the Version number depending on the contents of your branch and create a pull request to the respective release branch.

## Creating a new release
Execute the following steps in order to create a new DiscoPoP release:
- Switch to the release branch (e.g. `release/1.2.3`) which shall be released
- Update the version files in the repository
- Create a pull request to the `master` branch and validate the changes
- Merge the pull request and create a tag on the `master` branch with the name `v1.2.3`
    - Creating the tag triggers the automatic publication of the project to PyPi
    - Creating the tag triggers the automatic creation of a release draft
- Update the newly created release draft
  - Release tag: `v1.2.3`
  - Release title: `Version 1.2.3`
  - Description should contain a summary of the most relevant changes
- If everything is fine, publish the new release

### Determining the Version Number
Lets assume a current version number `1.2.3`.
A new version number shall be determined as follows:
* Release only contains Bugfixes and minor improvements (e.g. code cleanup, stability fixes etc.) or documentation updates.
    * ==> Increase the last digit by `1`
* Release adds / modifies features with only a relatively minor impact (e.g. adding a new flag), <b>while ensuring full compatibility</b> with the previous version.
    * ==> Increase middle digit by `1`.
    * ==> Set last digit to `0`.
* Release adds a major new feature or modifies any interface (for example by modifying the format of input or output data) in such a way that it is <b>not fully compatible</b> with the previous version anymore.
    * ==> Increase first digit by `1`.
    * ==> Set remaining digits to `0`.