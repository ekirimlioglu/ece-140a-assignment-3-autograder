import unittest
from playwright.sync_api import sync_playwright
from gradescope_utils.autograder_utils.decorators import weight


class TestPuppyPongCSS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up Playwright and browser instance before all tests."""
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.firefox.launch(headless=True)
        cls.page = cls.browser.new_page()
        # Set viewport size to ensure consistent testing
        cls.page.set_viewport_size({"width": 1024, "height": 768})

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests are done."""
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        """Navigate to the puppy pong page before each test"""
        self.page.goto("http://localhost:6543/puppy-pong")

    @weight(3)
    def test_01_body_styles(self):
        """Test if body has correct background color and height"""
        body_styles = self.page.evaluate(
            """
            () => {
                const body = document.body;
                const styles = window.getComputedStyle(body);
                const windowHeight = window.innerHeight;
                const bodyHeight = body.clientHeight;
                return {
                    backgroundColor: styles.backgroundColor,
                    height: bodyHeight,
                    windowHeight: windowHeight
                };
            }
        """
        )

        # Compare background color directly
        self.assertEqual(
            body_styles["backgroundColor"],
            "rgb(34, 34, 34)",  # #222 in RGB
            "Body background color should be #222",
        )

        # Check body height matches window height
        self.assertEqual(
            body_styles["height"],
            body_styles["windowHeight"],
            "Body height should match window height",
        )

    @weight(3)
    def test_02_absolute_positioning(self):
        """Test if puppy image and death zone are absolutely positioned"""
        positioning = self.page.evaluate(
            """
            () => {
                const img = document.querySelector('img');
                const deathzone = document.querySelector('#deathzone');
                const imgStyles = window.getComputedStyle(img);
                const deathzoneStyles = window.getComputedStyle(deathzone);
                return {
                    imgPosition: imgStyles.position,
                    deathzonePosition: deathzoneStyles.position
                };
            }
        """
        )

        self.assertEqual(
            positioning["imgPosition"],
            "absolute",
            "Puppy image should be absolutely positioned",
        )
        self.assertEqual(
            positioning["deathzonePosition"],
            "absolute",
            "Death zone should be absolutely positioned",
        )

    @weight(3)
    def test_03_deathzone_styles(self):
        """Test if death zone has correct styles"""
        deathzone_styles = self.page.evaluate(
            """
            () => {
                const deathzone = document.querySelector('#deathzone');
                const styles = window.getComputedStyle(deathzone);
                return {
                    backgroundColor: styles.backgroundColor,
                    width: deathzone.clientWidth,
                    windowWidth: window.innerWidth,
                    bottom: styles.bottom
                };
            }
        """
        )

        # Check background color (black)
        self.assertEqual(
            deathzone_styles["backgroundColor"],
            "rgb(0, 0, 0)",
            "Death zone background color should be black",
        )

        # Check width matches window width
        self.assertEqual(
            deathzone_styles["width"],
            deathzone_styles["windowWidth"],
            "Death zone width should match window width",
        )

        # Check position at bottom
        self.assertEqual(
            deathzone_styles["bottom"],
            "0px",
            "Death zone should be at the bottom of the browser",
        )

    @weight(3)
    def test_04_text_and_player_colors(self):
        """Test if paragraphs have white text and player has white background"""
        colors = self.page.evaluate(
            """
            () => {
                const paragraphs = document.querySelectorAll('p');
                const player = document.querySelector('#player');
                const playerStyles = window.getComputedStyle(player);

                // Get all paragraph colors
                const paragraphColors = Array.from(paragraphs).map(p =>
                    window.getComputedStyle(p).color
                );

                return {
                    paragraphColors: paragraphColors,
                    playerBackgroundColor: playerStyles.backgroundColor
                };
            }
        """
        )

        # Check paragraph text colors
        for i, color in enumerate(colors["paragraphColors"]):
            self.assertEqual(
                color,
                "rgb(255, 255, 255)",  # white in RGB
                f"Paragraph {i+1} should have white text color",
            )

        # Check player background color
        self.assertEqual(
            colors["playerBackgroundColor"],
            "rgb(255, 255, 255)",
            "Player should have white background color",
        )
