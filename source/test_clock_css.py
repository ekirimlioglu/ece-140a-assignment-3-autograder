import unittest
from playwright.sync_api import sync_playwright
from gradescope_utils.autograder_utils.decorators import weight, visibility


class TestWorldClockCSS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up Playwright and browser instance before all tests."""
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.firefox.launch(headless=True)
        cls.page = cls.browser.new_page()
        cls.page.set_viewport_size({"width": 1024, "height": 768})

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests are done."""
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        """Navigate to the world clock page before each test."""
        self.page.goto("http://localhost:6543/world-clock")

    @weight(3)
    @visibility("visible")
    def test_01_input_background_color(self):
        """[Extra] Test if input elements have pink background color"""
        # Get computed style for both text and number inputs
        background_colors = self.page.evaluate(
            """
            () => {
                const inputs = document.querySelectorAll('input[type="submit"]');
                return Array.from(inputs).map(input =>
                    window.getComputedStyle(input).backgroundColor
                );
            }
        """
        )

        # Check if all inputs have pink background
        for color in background_colors:
            self.assertEqual(
                color.lower(),
                "rgb(255, 192, 203)",  # pink in RGB
                "Input elements should have pink background color",
            )

    @weight(3)
    @visibility("visible")
    def test_02_input_hover_color(self):
        """[Extra] Test if input elements have aqua background color on hover"""
        # Get all text and number inputs
        inputs = self.page.locator('input[type="submit"]')

        # Test each input's hover state
        for i in range(inputs.count()):
            input_elem = inputs.nth(i)

            # Hover over the input
            input_elem.hover()
            self.page.wait_for_timeout(100)  # Small delay to ensure hover is applied

            # Get the computed background color after hover
            hover_color = input_elem.evaluate(
                """element =>
                window.getComputedStyle(element).backgroundColor
            """
            )

            self.assertEqual(
                hover_color.lower(),
                "rgb(0, 255, 255)",  # aqua in RGB
                f"Input element {i + 1} should have aqua background color on hover",
            )

    @weight(9)
    @visibility("visible")
    def test_03_clock_grid_layout(self):
        """[Extra] Test if clocks use CSS grid with correct properties"""
        # Check grid properties using JavaScript evaluation
        grid_properties = self.page.evaluate(
            """
            () => {
                const clocksContainer = document.querySelector('#clocks');
                const styles = window.getComputedStyle(clocksContainer);
                return {
                    display: styles.display,
                    gridTemplateColumns: styles.gridTemplateColumns,
                    gridTemplateRows: styles.gridTemplateRows,
                    gridAutoFlow: styles.gridAutoFlow
                };
            }
        """
        )

        # Check if display is grid
        self.assertEqual(
            grid_properties["display"],
            "grid",
            "Clocks container should use CSS grid display",
        )

        # Check grid template columns (5 columns of 240px)
        expected_columns = "240px" in grid_properties["gridTemplateColumns"]
        self.assertTrue(expected_columns, "Grid should have 5 columns of 240px each")

        # Check grid template rows (2 rows of 120px)
        expected_rows = "120px" in grid_properties["gridTemplateRows"]
        self.assertTrue(expected_rows, "Grid should have 2 rows of 120px each")

        # Check grid auto flow
        self.assertEqual(
            grid_properties["gridAutoFlow"],
            "row",
            "Grid auto-flow should be set to row",
        )
