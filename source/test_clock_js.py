import unittest
from playwright.sync_api import sync_playwright
from gradescope_utils.autograder_utils.decorators import weight


class TestWorldClockJavaScript(unittest.TestCase):
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
        """Navigate to the world clock page and wait for it to load before each test"""
        self.page.goto("http://localhost:6543/world-clock")

        # try:
        #     # Wait for timezone data to be loaded
        #     self.page.wait_for_function(
        #         """
        #         () => {
        #             return window.time_diffs !== undefined;
        #         }
        #     """,
        #         timeout=5000,
        #     )
        # except TimeoutError:
        #     self.fail("time_diffs is undefined")

    @weight(5)
    def test_01_empty_form_submission(self):
        """Test that empty forms cannot be submitted"""
        # Try to submit empty timezone form
        timezone_form = self.page.locator("form").first
        timezone_form.locator("input[type='submit']").click()

        # Check that no clock was added
        clocks = self.page.locator("ul#clocks li")
        self.assertEqual(clocks.count(), 0, "No clock should be added with empty input")

        # Try to submit empty index form
        index_form = self.page.locator("form").nth(1)
        index_form.locator("input[type='submit']").click()

        # Verify no errors occurred
        self.assertEqual(
            self.page.url,
            "http://localhost:6543/world-clock",
            "Page should remain on same URL after empty form submission",
        )

    @weight(5)
    def test_02_invalid_timezone_submission(self):
        """Test that invalid timezone input doesn't add a clock"""
        # Submit invalid timezone
        timezone_form = self.page.locator("form").first
        timezone_input = timezone_form.locator("input[type='text']")

        timezone_input.fill("INVALID")
        timezone_form.locator("input[type='submit']").click()

        # Check that no clock was added
        clocks = self.page.locator("ul#clocks li")
        self.assertEqual(
            clocks.count(), 0, "No clock should be added with invalid timezone"
        )

    @weight(5)
    def test_03_valid_timezone_submission(self):
        """Test that valid timezone input adds a clock"""
        # Submit valid timezone
        timezone_form = self.page.locator("form").first
        timezone_input = timezone_form.locator("input[type='text']")

        timezone_input.fill("PST")
        timezone_form.locator("input[type='submit']").click()

        try:
            # Wait for the clock to be added with 5 second timeout
            self.page.wait_for_selector("ul#clocks li", timeout=5000)
        except TimeoutError:
            self.fail("Clock element was not added within 5 seconds")

        # Verify clock was added with correct structure
        clocks = self.page.locator("ul#clocks li")
        self.assertEqual(clocks.count(), 1, "One clock should be added")

        # Verify clock has required elements
        clock = clocks.first
        self.assertTrue(
            clock.locator("div.timezone").is_visible(), "Clock should have timezone div"
        )
        self.assertTrue(
            clock.locator("div.offset").is_visible(), "Clock should have offset div"
        )
        self.assertTrue(
            clock.locator("div.time").is_visible(), "Clock should have time div"
        )

        # Verify input was cleared
        self.assertEqual(
            timezone_input.input_value(), "", "Input should be cleared after submission"
        )

    @weight(5)
    def test_04_valid_index_removal(self):
        """Test that valid index removes correct clock"""
        # First add a clock
        timezone_form = self.page.locator("form").first
        timezone_input = timezone_form.locator("input[type='text']")
        timezone_input.fill("PST")
        timezone_form.locator("input[type='submit']").click()

        try:
            # Wait for clock to be added with 5 second timeout
            self.page.wait_for_selector("ul#clocks li", timeout=5000)
        except TimeoutError:
            self.fail("Clock element was not added within 5 seconds")

        # Submit valid index to remove
        index_form = self.page.locator("form").nth(1)
        index_input = index_form.locator("input[type='number']")
        index_input.fill("1")
        index_form.locator("input[type='submit']").click()

        # Check that clock was removed
        clocks = self.page.locator("ul#clocks li")
        self.assertEqual(clocks.count(), 0, "Clock should be removed")

        # Verify input was cleared
        self.assertEqual(
            index_input.input_value(), "", "Input should be cleared after submission"
        )

    @weight(5)
    def test_05_invalid_index_removal(self):
        """Test that invalid index doesn't remove any clocks"""
        # First add a clock
        timezone_form = self.page.locator("form").first
        timezone_input = timezone_form.locator("input[type='text']")
        timezone_input.fill("PST")
        timezone_form.locator("input[type='submit']").click()

        # Wait for clock to be added
        self.page.wait_for_selector("ul#clocks li")

        # Submit invalid index
        index_form = self.page.locator("form").nth(1)
        index_input = index_form.locator("input[type='number']")
        index_input.fill("9")  # Index out of range
        index_form.locator("input[type='submit']").click()

        # Check that clock was not removed
        clocks = self.page.locator("ul#clocks li")
        self.assertEqual(
            clocks.count(), 1, "Clock should not be removed with invalid index"
        )
