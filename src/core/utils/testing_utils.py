"""Utility classes/functions useful for testing throughout the project"""
from __future__ import annotations
import logging.handlers
import platform
import logging
import traceback

from django.test import LiveServerTestCase, tag
from rest_framework.test import APITestCase

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


from user_management.models import Author
from posts.models import Post, PostTypes, VisibilityTypes


@tag("api")
class GeneralUserStoryApiTest(APITestCase):
    def setUp(self) -> None:
        self.author = Author.local_authors.create_author(
            username="testuser", password="testpassword", display_name="Mr Test")
        self.client.force_authenticate(user=self.author.user)
        self.sample_authors: list[Author] = []
        self.sample_posts: list[list[Post]] = []
        # to get the posts of the sample authors (if initialized), use self.sample_authors[author_index].posts

    def initialize_sample_authors(self, num_authors: int = 5) -> None:
        """Initialize some sample authors for testing"""
        for i in range(num_authors):
            author = Author.local_authors.create_author(
                username=f"testuser{i}", password="testpassword", display_name=f"Mr Test {i}")
            self.sample_authors.append(author)

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


@tag("ui")
class UITestCase(LiveServerTestCase):
    """Testing class for UI tests that require a live server
    - all UI tests should:
        - spawn a firefox browser
        - interact using the public `self.*` methods, **Not `driver.* methods`!**
            - *Important: this is because these methods log the actions taken (printing them out on failure), and make debugging the tests orders of magnitude easier*
            - If what you need to do is not covered by the public methods, please add a new one, and follow the same pattern :)

    Some functionality (_get_driver(), logging) was pulled from my 401 project, and modified to fit the proper standards of this project"""

    def _get_driver(self) -> webdriver.Firefox:
        is_actions_runner = platform.node() == "gh-actions-runner"
        if is_actions_runner:
            geckodriver_path = "/snap/bin/geckodriver"

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
            capacity=5000, flushLevel=logging.ERROR, target=stream_handler)
        memory_handler.setLevel(logging.DEBUG)
        memory_handler.setFormatter(formatter)
        logger.addHandler(memory_handler)
        return logger

    def setUp(self) -> None:
        self.driver = self._get_driver()
        self.logger = self._get_logger()

    # ======================= PUBLIC UTILITY METHODS START HERE =======================

    # --------- Action methods --------------
    def log(self, message: str, level: int = logging.INFO) -> None:
        """Log a message with a certain level, and an indentation level based on the *current stack depth*"""
        indentation_level = max(
            len(traceback.extract_stack()) - self._logging_stack_start_depth, 0)
        indentation = " " + "---" * indentation_level + " "
        self.logger.log(level, f"{indentation}{message}")

    def visit(self, url: str, validate_html: bool = True) -> None:
        """Visit a URL, optionally validate the HTML (this may add a delay)"""
        self.log(f"Visiting {url}")
        self.driver.get(url)
        if validate_html:
            # TODO wait for everything to load? then validate the HTML
            pass

    # --------- Find element methods --------------
    def find_element_by_id(self, element_id: str) -> WebElementLoggingWrapper:
        """Find an element by its ID"""
        self.log(f"Finding element by ID: {element_id}")
        element = self.driver.find_element(by=By.ID, value=element_id)
        return WebElementLoggingWrapper(element, self)

    def find_element_by_name(self, element_name: str) -> WebElementLoggingWrapper:
        """Find an element by its name"""
        self.log(f"Finding element by name: {element_name}")
        element = self.driver.find_element(by=By.NAME, value=element_name)
        return WebElementLoggingWrapper(element, self)

    def find_elements_by_name(self, element_name: str) -> list[WebElementLoggingWrapper]:
        """Find elements by their name"""
        self.log(f"Finding elements by name: {element_name}")
        elements = self.driver.find_elements(by=By.NAME, value=element_name)
        output: list[WebElementLoggingWrapper] = []
        for element in elements:
            output.append(WebElementLoggingWrapper(element, self))
        return output

    # --------- Assertion methods --------------
    def assert_title(self, expected_title: str) -> None:
        """Assert that the title of the page is as expected"""
        self.log(f"Asserting title is: {expected_title}")
        self.assertEqual(self.driver.title, expected_title)

    def assert_path(self, expected_path: str) -> None:
        """Assert that the path of the page is as expected"""
        self.log(f"Asserting path is: {expected_path}")
        self.assertEqual(self.driver.current_url,
                         self.live_server_url + expected_path)

    def assert_id_exists(self, element_id: str) -> None:
        """Assert that an element with the given ID exists"""
        self.log(f"Asserting element with ID exists: {element_id}")
        try:
            self.find_element_by_id(element_id)
        except NoSuchElementException:
            self.fail(f"Element with ID {element_id} does not exist")

    def assert_id_not_exists(self, element_id: str) -> None:
        """Assert that an element with the given ID does not exist"""
        self.log(f"Asserting element with ID does not exist: {element_id}")
        with self.assertRaises(NoSuchElementException):
            self.find_element_by_id(element_id)
