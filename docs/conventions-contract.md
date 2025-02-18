## Naming Conventions
### Programming
- Modules/files 
- Classes (I prefer PascalCase)
	- *Class names must never start with a verb*
- Functions (I prefer snake_case)
	- *General functions must start with a verb, and clearly state what they do*
		- exceptions are things like class functions decorated with `@property` (Python specific)
	- `user.re_fetch_online_data()` is good
	- `user.username()` is not good, `.username` looks like an instance variable
		- The `@property` decorator might be useful here, if you wanted to write a username getter (Python specific) 
	- `figure_out_thing()` is likewise not good, other people would have no idea what it does without looking into the implementation
- Variables (I prefer snake_case)
	- *Variables must never start with a verb*
	- **Variables must not have super short names like `b1`**
		- Exceptions: *list comprehensions, `for` loop counters, and caught exceptions only*
			- Loop counters can be things like `i, j, k, l`,
			- Exceptions can be `e`
			- Even with while loops, try to use a proper counter name that explains what its stepping through, eg: `user_index`
	- Variables referencing physical values must have a unit associated with them
		- eg: `length_mm` instead of `length`
		- If this is not possible, units must be in a comment at the declaration of the variable

### Source control 

> [!NOTE] 
> Commit/Branch Types
> - `feat`: A new feature
> - `fix`: A bug fix
> - `docs`: Documentation changes (e.g., `README`, inline comments)
> - `refactor`: Code changes that neither fix a bug nor add a feature
> - `perf`: Performance improvements
> - `test`: Adding or updating tests
> - `ci`: Changes to CI/CD configuration files and scripts (github actions)
> - `chore`: Maintenance tasks, like dependency upgrades or cleanup


#### Commit Conventions
Format: `<type>(optional scope): <description>`

*Incremental commits must still use these guidelines, eg: `feat: partial implementation of xyz: added x, changed y`* 

If you want to specify a particular part of the project the commit changes  (ui, auth, database, etc), use scopes:

Examples:
- With scopes: `feat(api): add user authentication`
- Without scopes: `refactor: move validation code to separate function`

#### Branch conventions
Format: `<type>/(optional issue#<issue-number>)-<short-description>`
- The type will usually be `feat`, but you can use any of them

If there is no user story issue to close with your branch, you can just omit the user story number

Examples:
- With issue number: `feat/issue#13-remove-images`
- Without issue number: `fix/button-overlap-issue`

#### Pull Requests
*Don't create an open PR until your code is ready to merge, if you want to check for any merging issues, use a draft PR*

After creating a PR, Make sure to click on the "closes issue" button, or whatever it is called, and pick the user story/issue it closes.

It will be reviewed by someone else - they can add comments to specific lines of code. You can then go and commit and push changes to your branch, and they will be  reflected in the PR. Then it can be closed and merged by someone else. Once it's merged the issue will be closed automatically.

## Programming Conventions
- In dynamically typed languages that support it, use strict type hint checking
	- (Takes a little time to declare function types, etc, but saves so much time down the road when revisiting code)
- Always avoid multiple sources of truth unless absolutely necessary
- Code should be easy to read and follow from the POV of someone who did not write it
- The path to a piece of code must be logical, each `.` (or `::`) should lower the scope
	- `DatabaseModels.User.get_username()` makes sense
	- `DatabaseModels.get_username_of_user(user)` is a little general, don't do this if you can help it
	- `DatabseModels.ShopItem.get_username(user)` doesn't make sense
- If you are going to copy paste more than a single uncomplicated line, *heavily* consider extracting to a function or class
	- AI likes to do this, so be careful if you use it!
	- Likewise, if you are writing something you think could be reused in the future, heavily consider putting it in a function or class.
	- (Helps with multiple sources of truth issue)
- Don't hardcode any data in production level code, use config files 
	- Config files as code (eg `settings.py`) is okay, as long as they don't contain logic beyond what is needed to declare the configuration
	- (Also helps with the multiple sources of truth issue)
- When the language allows it, use trailing commas for multi-line data structures, and put the closing bracket on a newline
	- eg:
	```
	list = [something_long,
	        something_long2,
	        something_long3,
	        ]
	```
	- (Makes merge conflicts less likely and easier to deal with)
### Functions
- Functions must be relevant to everything in their scope, this gets more important with lower and lower scopes
	- i.e. if you have a function at the top level of a file, it must be important to everything in that file, or be there for a very good reason
	- If a function feels too specific, consider splitting into a new file
- Functions longer than a few lines should have documentation associated with them explaining what they do, ideally in the standard method for the language
	- especially important for functions other people will use
	- for Python and Vs Code, I recommend the [autoDocString](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring) extension
		- write your function header, then press control+shift+2 and it'll make it for you

### Variables
- in dynamically typed languages, A variable's type should stay consistent throughout its use
	- with the exception of changing to/from `None` or `Null` types
	- eg if `name` is a python string:
		- `name_letters = list(name)` is good
		- `name = list(name)` is bad (string $\to$ list, harder to reason about types later)
- Variable names should be ordered in descending significance
	- `latency_ms_min` is good (latency is topic, milliseconds is unit, min is qualifier)
		- searching for `latency_` will return all variables that are "descendants" of latency
	- `min_ms_latency` is not as good, it won't visually line up with other `latency` related variables, and the search won't work as well

## Dev Ops Conventions
### Source Control
- Commit often and with descriptive messages (see [Source Control](#source-control) for message conventions)
- Never commit to main, *always* work in branches
- A non-draft PR should be "ready to merge" following a review
	- i.e. you shouldn't have to ask the author if an open PR can be merged
- Always make your branches from the current "main" unless specifically required
- Have some way of claiming issues or work so two people can't work on the same thing separately
	
### Testing
- Get automated testing working as soon as possible within a project's timeline
- Spread tests into multiple files, by discretion
- Write classes to help write tests faster (consider what might be reused and extract that)
- *Whenever you fix a bug, write a test for it so that it can never be re-introduced*
- Don't re-test what's already been tested, all it does is bloat the code, and potentially add time to testing
	- eg: if you've already confirmed that querying a certain API endpoint will return properly structured data in all scenarios, all future tests can assume that the data will be properly structured
	- Exceptions to this are checks that exist inside test helper classes, but only those that take a negligible amount of time
		- eg: a helper class to navigate to different pages can assert that the page title is equal to what is expected after navigating, as it takes basically zero time to do

### Security
Use a clean/dirty data methodology
- All user data (including API input) is "dirty" and must be sanitized as soon as possible. 
- Functions that produce/consume dirty data must explicitly state it
- *Never* give dirty data to a function that doesn't explicitly state it can accept it

## Acknowledgements
- Some stylistic choices from the [[Tiger Style|Tiger Beetle Style Guide]] 
- Source control conventions from Rayvn's group, presentation format modified, draft pull request conventions added