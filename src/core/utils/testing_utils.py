"""Utility classes/functions useful for testing throughout the project"""
from __future__ import annotations
import logging.handlers
import os
import logging
import traceback

from typing import Any, Never

from django.test import LiveServerTestCase, tag
from django.urls import reverse
from rest_framework.test import APITestCase

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from user_management.models import Author, JoinRequest
from posts.models import Post, PostTypes, VisibilityTypes


@tag("api")
class GeneralUserStoryApiTest(APITestCase):
    def setUp(self) -> None:
        self.author = Author.local_authors.create_author(
            username="testuser", password="testpassword", display_name="Mr Test")
        self.client.force_authenticate(user=self.author.user)
        self.sample_authors: list[Author] = []
        self.sample_author_passwords: list[str] = []
        self.sample_posts: list[list[Post]] = []
        # to get the posts of the sample authors (if initialized), use self.sample_authors[author_index].posts

    def initialize_sample_authors(self, num_authors: int = 5) -> None:
        """Initialize some sample authors for testing"""
        for i in range(num_authors):
            author = Author.local_authors.create_author(
                username=f"testuser{i}", password="testpassword", display_name=f"Mr Test {i}")
            self.sample_authors.append(author)
            self.sample_author_passwords.append("testpassword")

    def initialize_sample_text_posts(self,
                                     posts_per_author: int = 1,
                                     visibility_type: VisibilityTypes = VisibilityTypes.PUBLIC,
                                     post_type: PostTypes = PostTypes.PLAINTEXT
                                     ) -> None:
        """Initialize some sample text posts for the sample authors

        Args:
            posts_per_author (int, optional): number of posts each author will "make". Defaults to 1.
            visibility_type (socialmodels.PostTextBased.VisibilityTypes, optional): visibility type of generated posts. Defaults to socialmodels.PostTextBased.VisibilityTypes.PUBLIC.
            post_type (socialmodels.PostTextBased.TextPostTypes, optional): post type of posts. Defaults to socialmodels.PostTextBased.TextPostTypes.PLAINTEXT.
        """
        for author in self.sample_authors:
            author_posts: list[Post] = []
            for i in range(posts_per_author):
                post = Post.objects.create_post(
                    author=author,
                    title=f"Sample post {i}",
                    description=f"Description {i}",
                    content=f"This is {author.display_name}'s post {i}",
                    visibility_type=visibility_type,
                    post_type=post_type,
                )
                author_posts.append(post)
            if len(self.sample_posts) < len(self.sample_authors):
                self.sample_posts.append(author_posts)
            else:
                self.sample_posts[i].extend(author_posts)


class WebElementLoggingWrapper:
    """A wrapper around a web element that logs all actions taken on it :)

    If it's missing an action you need, please add it and follow the same pattern!"""

    def __init__(self, element: WebElement, test_case: UITestCase) -> None:
        self.element = element
        self.test_case = test_case

    def __str__(self) -> str:
        return str(self.element)

    def click(self) -> None:
        self.test_case.log(f"{self}: Clicking")
        self.element.click()

    def send_keys(self, keys: str) -> None:
        self.test_case.log(f"{self}: Sending keys: {keys}")
        self.element.send_keys(keys)

    def clear(self) -> None:
        self.test_case.log(f"{self}: Clearing")
        self.element.clear()


@tag("ui")
class UITestCase(LiveServerTestCase, GeneralUserStoryApiTest):
    """Testing class for UI tests that require a live server
    - all UI tests should:
        - spawn a firefox browser
        - interact using the public `self.*` methods, **Not `driver.* methods`!**
            - *Important: this is because these methods log the actions taken (printing them out on failure), and make debugging the tests orders of magnitude easier*
            - If what you need to do is not covered by the public methods, please add a new one, and follow the same pattern :)
        - end your test with `self.end_test()` to close the browser

    Some functionality (_get_driver(), logging) was pulled from my 401 project, and modified to fit the proper standards of this project"""

    def _get_driver(self) -> webdriver.Firefox:
        # https://stackoverflow.com/questions/73973332/check-if-were-in-a-github-action-travis-ci-circle-ci-etc-testing-environme
        self.is_in_github_actions = bool(os.getenv("GITHUB_ACTIONS"))
        if self.is_in_github_actions:
            # grab the installded geckodriver version (will be installed on the runner by the django-tests.yml before this is run)
            geckodriver_root = "/opt/hostedtoolcache/geckodriver"
            geckodriver_version = os.listdir(geckodriver_root)[0]
            geckodriver_path = f"{geckodriver_root}/{geckodriver_version}/x64/geckodriver"

            driver_service = webdriver.FirefoxService(
                executable_path=geckodriver_path)

            options = webdriver.FirefoxOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--headless')
            # https://stackoverflow.com/questions/15397483/how-to-set-browsers-width-and-height-in-selenium-webdriver
            options.add_argument('--width=1920')
            options.add_argument('--height=1080')

            return webdriver.Firefox(service=driver_service, options=options)
        else:
            return webdriver.Firefox(options=webdriver.FirefoxOptions())

    def _get_logger(self) -> logging.Logger:
        """Set up a logger for the test case"""
        logger = logging.getLogger(
            f"UITestCase:{self._testMethodName}")
        formatter = logging.Formatter(
            "[ %(levelname)8s ] %(message)s")
        logger.setLevel(logging.DEBUG)

        # this is the depth of the stack when the test starts
        self._logging_stack_start_depth = len(traceback.extract_stack()) - 1

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)
        memory_handler = logging.handlers.MemoryHandler(
            capacity=5000, flushLevel=logging.ERROR, target=stream_handler, flushOnClose=False)
        memory_handler.setLevel(logging.DEBUG)
        memory_handler.setFormatter(formatter)
        logger.addHandler(memory_handler)
        # when the handler is flushed it doesn't put a newline at the beginning, so this makes it nicer to read
        logger.info("Test Started")
        return logger

    def setUp(self) -> None:
        self.driver = self._get_driver()
        self.logger = self._get_logger()
        super().setUp()

    def fail(self, msg: Any = ...) -> Never:
        """Fail the test"""
        self.logger.critical("Test Failed")
        super().fail(msg)

    def end_test(self) -> None:
        self.driver.quit()

    # ======================= PUBLIC UTILITY METHODS START HERE =======================

    # --------- Action methods --------------

    def log(self, message: str, level: int = logging.INFO, indentation_offset: int = 0) -> None:
        """Log a message with a certain level, and an indentation level based on the *current stack depth relative to the start* + `indentation_offset`"""
        # you would want to use an indentation_offset=-1 if you're logging the start of a group of actions, and leave it at 0 otherwise
        # eg: see the `login_as` method
        indentation_level = max(
            len(traceback.extract_stack()) + indentation_offset - self._logging_stack_start_depth, 0)
        indentation = " " + "---" * indentation_level + " "
        self.logger.log(level, f"{indentation}{message}")

    def visit(self, url: str, relative_url: bool = True, validate_html: bool = True) -> None:
        """Visit a URL

        eg: `visit("/admin")` will visit the admin panel (local_server_url/admin)
        eg: `visit("https://google.com", relative_url=False)` will visit google.com

        Args:
            url (str): url to visit
            relative_url (bool, optional): if True, the URL will be appended to the live server URL. Defaults to True.
            validate_html (bool, optional): check HTML validity upon visiting. Defaults to True.
        """
        if relative_url:
            url = self.live_server_url + url
        self.log(f"Visiting {url}", indentation_offset=-1)
        self.driver.get(url)
        if validate_html:
            self.validate_html()

    def validate_html(self) -> None:
        """Validate the HTML of the current page, raise an exception if it's invalid"""
        self.log("Validating HTML", indentation_offset=-1)
        pass  # TODO

    def login_as(self, author: Author) -> None:
        """Log in as an author"""
        self.log(f"Logging in as {author.username}", indentation_offset=-1)
        if not author.user:
            self.fail("Author does not have a user")
        self.visit(reverse("user_management:login"))
        try:
            author_index = self.sample_authors.index(author)
        except ValueError:
            raise Exception(
                "You can only log in as a sample author, we can't fetch the password otherwise")
        self.find_element_by_id("id_username").send_keys(author.username)
        self.find_element_by_id("id_password").send_keys(self.sample_author_passwords[author_index])
        self.find_elements_by_selector("input[type=submit]")[0].click()

    def log_out(self) -> None:
        """Log out of the current session"""
        self.log(f"Logging out", indentation_offset=-1)
        self.client.logout()

    # --------- Find element methods --------------
    def _find_element(self, by: str, value: str) -> WebElementLoggingWrapper:
        """Find an element by a given method"""
        try:
            element = self.driver.find_element(by=by, value=value)
        except NoSuchElementException:
            self.fail(f"Element not found by {by}: {value}")
        return WebElementLoggingWrapper(element, self)

    def find_element_by_id(self, element_id: str) -> WebElementLoggingWrapper:
        """Find an element by its ID"""
        self.log(f"Finding element by ID: {element_id}", indentation_offset=-1)
        return self._find_element(by=By.ID, value=element_id)

    def find_element_by_name(self, element_name: str) -> WebElementLoggingWrapper:
        """Find an element by its name"""
        self.log(f"Finding element by name: {element_name}", indentation_offset=-1)
        return self._find_element(by=By.NAME, value=element_name)

    def find_elements_by_name(self, element_name: str) -> list[WebElementLoggingWrapper]:
        """Find elements by their name"""
        self.log(f"Finding elements by name: {element_name}", indentation_offset=-1)
        elements = self.driver.find_elements(by=By.NAME, value=element_name)
        output: list[WebElementLoggingWrapper] = []
        for element in elements:
            output.append(WebElementLoggingWrapper(element, self))
        self.log(f"Found {len(output)} elements")
        return output

    def find_elements_by_selector(self, selector: str) -> list[WebElementLoggingWrapper]:
        """Find elements by a CSS selector, **Do not use unless absolutely necessary**"""
        self.log(f"Finding elements by selector: {selector}", indentation_offset=-1)
        elements = self.driver.find_elements(by=By.CSS_SELECTOR, value=selector)
        output: list[WebElementLoggingWrapper] = []
        for element in elements:
            output.append(WebElementLoggingWrapper(element, self))
        self.log(f"Found {len(output)} elements")
        return output

    def find_elements_by_value(self, value: str) -> list[WebElementLoggingWrapper]:
        """Find elements by their value"""
        self.log(f"Finding elements by value: {value}", indentation_offset=-1)
        elements = self.driver.find_elements(by=By.XPATH, value=f"//*[@value='{value}']")
        output: list[WebElementLoggingWrapper] = []
        for element in elements:
            output.append(WebElementLoggingWrapper(element, self))
        self.log(f"Found {len(output)} elements")
        return output

    # --------- Waiting methods --------------
    def wait_for_element_by_id(self, element_id: str, timeout: int = 10) -> WebElementLoggingWrapper:
        """Wait for an element by its ID to appear"""
        # Created by Copilot: wait for an element by its ID to appear
        self.log(f"Waiting for element by ID: {element_id}", indentation_offset=-1)
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, element_id))
            )
            return WebElementLoggingWrapper(element, self)
        except Exception as e:
            self.fail(f"Element with ID {element_id} did not appear: {e}")

    # --------- Assertion methods --------------
    def assert_title(self, expected_title: str) -> None:
        """Assert that the title of the page is as expected"""
        self.log(f"Asserting title is: {expected_title}", indentation_offset=-1)
        self.assertEqual(self.driver.title, expected_title)

    def assert_path(self, expected_path: str) -> None:
        """Assert that the path of the page is as expected"""
        self.log(f"Asserting path is: {expected_path}", indentation_offset=-1)
        self.assertEqual(self.driver.current_url,
                         self.live_server_url + expected_path)

    def assert_id_exists(self, element_id: str) -> None:
        """Assert that an element with the given ID exists"""
        self.log(f"Asserting element with ID exists: {element_id}", indentation_offset=-1)
        try:
            self.find_element_by_id(element_id)
        except NoSuchElementException:
            self.fail(f"Element with ID {element_id} does not exist")

    def assert_id_not_exists(self, element_id: str) -> None:
        """Assert that an element with the given ID does not exist"""
        self.log(f"Asserting element with ID does not exist: {element_id}", indentation_offset=-1)
        with self.assertRaises(NoSuchElementException):
            self.find_element_by_id(element_id)


class AdminUITestCase(UITestCase):
    """Ui Test case for the admin panel, has some extra functionality for logging in as the admin user"""

    def setUp(self) -> None:
        self.admin_user = Author.local_authors.create_author(
            username="admin", password="admin", is_superuser=True)
        super().setUp()

    def login_as_admin(self) -> None:
        self.log("Logging in as admin", indentation_offset=-1)
        self.visit("/admin")
        if "Log in" in self.driver.title:
            self.find_element_by_name("username").send_keys("admin")
            self.find_element_by_name("password").send_keys("admin")
            self.find_elements_by_selector("input[type=submit]")[0].click()
            self.log("Logged in as admin")
        else:
            self.log("Already logged in")

    def adminpanel_set_action_to(self, action_name: str) -> None:
        self.log(f"Setting action to: {action_name}", indentation_offset=-1)
        try:
            action_dropdown = self.find_elements_by_selector("select[name=action]")[0]
        except IndexError:
            self.fail("No action dropdown found")
        action_dropdown_selector = Select(action_dropdown.element)
        try:
            action_dropdown_selector.select_by_visible_text(action_name)
        except NoSuchElementException:
            self.fail(f"No action with name {action_name} found")

    def adminpanel_do_action(self, action_name: str, confirm_needed: bool = False) -> None:
        """Do an action in the adminpanel models view (eg: Delete selected [model]s)
        If you are deleting, set confirm_needed=True so that it confirms the deletion"""
        self.log(f"Doing action: {action_name}", indentation_offset=-1)
        self.adminpanel_set_action_to(action_name)
        self.find_element_by_name("index").click()
        if confirm_needed:
            self.find_elements_by_selector("input[type=submit]")[0].click()
