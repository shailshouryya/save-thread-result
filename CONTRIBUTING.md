# Overview

To keep the project consistent with existing practices, follow the guidelines below. Minor deviations from the guidelines below may be accepted **sometimes** if following the guidleines is not possible or practical, but try following the suggestions below to the best of your ability as accepting changes that do not abide by the contributing suggestions will be rare and only for exceptional situations.


## Best Practices


### Submitting Pull Requests

When you submit a pull request, ensure your changes meet the following criteria:
- the pull request should be atomic and focus on a single change
- the pull request should include tests/examples for verifying the change
- the pull request should consider potential risks and potential mitigations for the changes
- the pull request should document the changes clearly and comprehensively
  - the changes should be broken up into small, atomic `git` commits that only make one logical change per commit
    - see the `git` commit message standards below
- the pull request does not include any unrelated small tweaks or changes

A pull request that does not follow the suggestions above will not be merged until the pull request is updated to abide by the contribution standards.

Additionally, a pull request that DOES follow the contribution standards above, BUT does not follow the standards for `git` commit messages outlined below will not be merged until the commit messages are updated to abide by the `git` commit message standards. Updating a `git` commit message requires rebasing your `git` commits (which can be quite confusing if you have not done any rebasing before) with something like `git rebase -i YOURCOMMITHASH` - if you are not sure how to do this, just try to follow the `git` commit message standards given below so you do not need to worry about this!


#### [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/) - [Chris Beams](https://chris.beams.io/); Aug 30, 2014

- Keep in mind:
  - [This](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)
  - [has](https://www.git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project#_commit_guidelines)
  - [all](https://github.com/torvalds/subsurface-for-dirk/blob/master/README.md#contributing)
  - [been](http://who-t.blogspot.co.at/2009/12/on-commit-messages.html)
  - [said](https://github.com/erlang/otp/wiki/writing-good-commit-messages)
  - [before](https://github.com/spring-projects/spring-framework/blob/30bce7/CONTRIBUTING.md#format-commit-messages).
1. Separate subject from body with a blank line
2. Limit the subject line to 50 characters
3. Capitalize the subject line
4. Do not end the subject line with a period
5. Use the imperative mood in the subject line
  - **A properly formed Git commit subject line should always be able to complete the following sentence**:
    - If applied, this commit will ***your subject line here***
  - For example:
    - If applied, this commit will ***refactor subsystem X for readability***
    - If applied, this commit will ***update getting started documentation***
    - If applied, this commit will ***remove deprecated methods***
    - If applied, this commit will ***release version 1.0.0***
    - If applied, this commit will ***merge pull request #123 from user/branch***
  - Notice how this doesn’t work for the other non-imperative forms:
    - If applied, this commit will ***fixed bug with Y***
    - If applied, this commit will ***changing behavior of X***
    - If applied, this commit will ***more fixes for broken stuff***
    - If applied, this commit will ***sweet new API methods***
6. Wrap the body at 72 characters
7. Use the body to explain what and why vs. how

Notes:
- all of the suggestions above seem reasonable and should be followed as much as possible
  - the only exception that will be exempted from here is the "Limit the subject line to 50 characters" rule
    - IF it is not possible to keep the commit message under 50 characters and still provide a good overview of what the commit does
      - for example, this is a commit message that cannot really be much shorter than it already is without making the commit message useless:
        - Rename `some_unreasonably_very_long_method_or_variable` → `less_long_but_clear_name`


### Reporting Bugs

If you find a bug in the project, create an issue on GitHub with the following information:
- a clear, descriptive title for the issue (using the same guidelines for formatting the title as the standards for formatting a subject of a commit message given above)
- a description of the problem along with the required steps to reproduce the issue
- any relevant logs, screenshots, code snippets, stack traces, and other supporting information


### Suggesting Enhancements

If you have an idea for a new feature or improvement, create an issue on GitHub with the following information:
- a clear, descriptive title for the issue (using the same guidelines for formatting the title as the standards for formatting a subject of a commit message given above)
- a detailed description of the proposed enhancement, including any benefits and potential drawbacks
- all relevant use cases, examples, mock-ups, and supporting information
