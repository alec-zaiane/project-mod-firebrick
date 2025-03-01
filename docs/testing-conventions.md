## Testing Conventions
When possible, all user stories should have a test file associated with it in `src/<app>/tests/test_US_##.py` (see `adminpanel/tests/test_US_44.py` as an example)
Remember, tasteful inheritance is your friend :)

### Test Tagging
Django supports [Test Tagging](https://docs.djangoproject.com/en/5.1/topics/testing/tools/#tagging-tests)
These can help us run tests faster by restricting the testing to a subset of all tests

They are also inherited from their parents (ie: if a testing class is tagged, all test methods receive the tag. also any classes extending it get tagged)

```python
from django.test import tag

@tag("check-fast", "user-story")
def test_dummy() -> None:
    self.assertTrue(True)
```


We'll have a few different tagging schemes:
- General tags
    - `api` for testing API related features
    - `bugfix` for if you fix a bug and want to make sure it cant re-occur
    - `security` for security related tests (eg access control)
    - ...

- User story categories
    - `US-identity`
    - `US-posting`
    - `US-reading`
    - `US-visibility`
    - `US-sharing`
    - `US-following/friends`
    - `US-comments/likes`
    - `US-node-management`

- Depth related tags 
    - (speed related words are referring to the speed to run all tagged tests, *not the speed of an individual test*, however if an individual test is slow, consider putting it in a slow group)
    - This is a little vibe-based, so there is grey area
    - `check-fast` for tests to be included in a "fast check"
        - The goal of this is to quickly see if you've broken something
        - Ideally not many tests will be in here, try to only tag the essentials as `speed-fast`
        - This should be verifying a very minimal MVP: if check-fast succeeds, a user who does everything perfectly should be able to use all the features of the app in a basic way
        - eg: Give an API good data and verify it did what it should
    - `check-medium` for tests to be included in a "medium speed check"
        - more stuff should go in here than `speed-fast`, but reserve the slower tests or in-depth ones for slower groups
        - eg: Give an API bad data and expect it to fail
    - `check-slow` for high amounts of in-depth tests, or tests you don't expect to ever be violated
        - eg: You fixed a bug and doubt it will come back, but you wrote a test to be sure
        - eg: You wrote lots of tests verifying access control permissions are respected
        - eg: Give an API bad data a bunch of times and expect it to fail properly in different ways
- 

