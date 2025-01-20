import unittest
from playwright.sync_api import sync_playwright
from gradescope_utils.autograder_utils.decorators import weight


class TestWorldClockPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up Playwright and browser instance before all tests."""
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.firefox.launch(headless=True)
        cls.page = cls.browser.new_page()

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests are done."""
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        """Navigate to the world clock page before each test."""
        self.page.goto("http://localhost:6543/world-clock")

    @weight(3)
    def test_01_form_elements(self):
        """Test if page has two forms with correct input elements"""
        # Check for exactly 2 forms
        forms = self.page.locator("form")
        self.assertEqual(forms.count(), 2, "Page should have exactly 2 forms")

        # Check first form inputs
        first_form = forms.nth(0)
        text_input = first_form.locator("input[type='text']")
        submit_input = first_form.locator("input[type='submit']")

        self.assertEqual(text_input.count(), 1, "First form should have one text input")
        self.assertEqual(
            submit_input.count(), 1, "First form should have one submit input"
        )

        # Check second form inputs
        second_form = forms.nth(1)
        number_input = second_form.locator("input[type='number']")
        submit_input = second_form.locator("input[type='submit']")

        self.assertEqual(
            number_input.count(), 1, "Second form should have one number input"
        )
        self.assertEqual(
            submit_input.count(), 1, "Second form should have one submit input"
        )

    @weight(2)
    def test_02_heading_element(self):
        """Test if page has correct h2 heading"""
        heading = self.page.locator("h2")
        self.assertEqual(heading.count(), 1, "Page should have exactly one h2 element")
        self.assertEqual(
            heading.inner_text(),
            "My Clocks",
            "h2 element should have text content 'My Clocks'",
        )

    @weight(2)
    def test_03_clocks_list(self):
        """Test if page has ul element with correct id"""
        clocks_list = self.page.locator("ul#clocks")
        self.assertEqual(
            clocks_list.count(),
            1,
            "Page should have exactly one ul element with id 'clocks'",
        )

    @weight(4)
    def test_04_template_structure(self):
        """Test if template element exists and has correct structure"""
        template = self.page.locator("template")
        self.assertEqual(
            template.count(), 1, "Page should have exactly one template element"
        )

        # Check template structure including li and all divs
        template_structure = self.page.evaluate(
            """
            () => {
                const template = document.querySelector('template');
                const content = template.content;
                const li = content.querySelector('li');

                return {
                    hasLi: li !== null,
                    hasTimezone: content.querySelector('li div.timezone') !== null,
                    hasOffset: content.querySelector('li div.offset') !== null,
                    hasTime: content.querySelector('li div.time') !== null
                };
            }
        """
        )

        self.assertTrue(
            template_structure["hasLi"], "Template should contain one li element"
        )
        self.assertTrue(
            template_structure["hasTimezone"],
            "Template should have one div with class 'timezone'",
        )
        self.assertTrue(
            template_structure["hasOffset"],
            "Template should have one div with class 'offset'",
        )
        self.assertTrue(
            template_structure["hasTime"],
            "Template should have one div with class 'time'",
        )

    @weight(3)
    def test_05_required_resources(self):
        """Test if required CSS and JavaScript files are included"""
        # Check if CSS link is in head using JavaScript evaluation
        css_in_head = self.page.evaluate(
            """
            () => {
                const cssLink = document.querySelector('link[href="/public/css/world_clock.css"]');
                return cssLink && cssLink.parentNode.tagName.toLowerCase() === 'head';
            }
        """
        )
        self.assertTrue(css_in_head, "CSS link should be in the head element")

        # Check if JavaScript script is last child of body using JavaScript evaluation
        js_is_last = self.page.evaluate(
            """
            () => {
                const body = document.body;
                const lastElement = body.lastElementChild;
                return lastElement &&
                       lastElement.tagName.toLowerCase() === 'script' &&
                       lastElement.src.endsWith('/public/js/world_clock.js');
            }
        """
        )
        self.assertTrue(
            js_is_last, "JavaScript script should be the last element in body"
        )
