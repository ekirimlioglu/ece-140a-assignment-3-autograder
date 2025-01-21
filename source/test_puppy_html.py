import unittest
from playwright.sync_api import sync_playwright
from gradescope_utils.autograder_utils.decorators import weight


class TestPuppyPongPage(unittest.TestCase):
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
        """Navigate to the puppy pong page before each test"""
        self.page.goto("http://localhost:6543/puppy-pong")

    @weight(5)
    def test_01_score_and_time_paragraphs(self):
        """Test if page has correct score and time paragraphs"""
        # Get all paragraphs
        paragraphs = self.page.locator("p")
        self.assertEqual(paragraphs.count(), 2, "Page should have exactly 2 paragraphs")

        # Check score paragraph format
        score_text = paragraphs.nth(0).inner_text()
        self.assertRegex(
            score_text,
            r"^Score: \d+$",
            "First paragraph should follow format 'Score: N'",
        )

        # Check time paragraph format
        time_text = paragraphs.nth(1).inner_text()
        self.assertRegex(
            time_text,
            r"^Time: \d+ secs$",
            "Second paragraph should follow format 'Time: N secs'",
        )

    @weight(5)
    def test_02_puppy_image(self):
        """Test if puppy image exists with correct attributes"""
        # Find image element
        img = self.page.locator("img[src='/public/puppy.jpg']")
        self.assertEqual(img.count(), 1, "Page should have exactly one puppy image")

        # Verify image attributes using JavaScript evaluation
        img_attributes = self.page.evaluate(
            """
            () => {
                const img = document.querySelector('img');
                return {
                    height: img.offsetHeight,
                    width: img.offsetWidth
                };
            }
        """
        )

        self.assertTrue(
            100 <= img_attributes["height"] <= 300, "Image height should be 200px"
        )
        self.assertTrue(
            200 <= img_attributes["width"] <= 400, "Image width should be 300px"
        )

    @weight(5)
    def test_03_deathzone_and_player(self):
        """Test if deathzone div and player span exist with correct IDs"""
        # Check deathzone div
        deathzone = self.page.locator("div#deathzone")
        self.assertEqual(
            deathzone.count(), 1, "Page should have exactly one div with id 'deathzone'"
        )

        # Check player span
        player = self.page.locator("span#player")
        self.assertEqual(
            player.count(), 1, "Page should have exactly one span with id 'player'"
        )

        # Verify player is inside deathzone using JavaScript evaluation
        player_in_deathzone = self.page.evaluate(
            """
            () => {
                const player = document.querySelector('#player');
                const deathzone = document.querySelector('#deathzone');
                return deathzone.contains(player);
            }
        """
        )
        self.assertTrue(
            player_in_deathzone, "Player span should be inside deathzone div"
        )

    @weight(5)
    def test_04_required_resources(self):
        """Test if required CSS and script are included"""
        # Check for CSS link in head
        css_in_head = self.page.evaluate(
            """
            () => {
                const cssLink = document.querySelector('link[href="/public/css/puppy_pong.css"]');
                return cssLink && cssLink.parentNode.tagName.toLowerCase() === 'head';
            }
        """
        )
        self.assertTrue(css_in_head, "CSS link should be in the head element")

        # Check for script element
        script = self.page.locator("script[src='/public/js/puppy_pong.js']")
        self.assertEqual(script.count(), 1, "Page should include puppy_pong.js script")
