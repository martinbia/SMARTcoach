"""Functional browser checks, served at the GitHub Pages repository subpath.

Run: python3 -m unittest discover -s tests -v
Requires Playwright and Chromium (see README). No application build required.
"""
import functools
import os
from pathlib import Path
import shutil
import threading
import tempfile
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        handler = functools.partial(QuietHandler, directory=str(ROOT.parent))
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}/{ROOT.name}/'
        cls.playwright = sync_playwright().start()
        executable = os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
        cls.browser = cls.playwright.chromium.launch(
            executable_path=executable, headless=True, args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1280, 'height': 800}, has_touch=True)
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.goto(self.url)

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def action(self, action):
        return self.page.locator(f'[data-action="{action}"]:visible')

    def home(self):
        self.action('home').click()
        self.page.locator('.journey-nodes').wait_for()

    def enable(self):
        self.action('companion').click()
        self.action('confirm-consent').click()

    def test_idle_navigation_and_event_sources(self):
        self.assertTrue(self.page.locator('.idle').is_visible())
        self.home()
        for event, title in [('J02', 'Operation'), ('J05', 'Austritt'), ('J09', 'Heute')]:
            self.action(f'event-{event}').click()
            expect(self.page.locator('h1')).to_have_text(title)
            self.assertIn('Demo', self.page.locator('.source').inner_text())
            self.action('home').first.click()
        self.assertTrue(self.page.locator('.journey-line path').get_attribute('d').startswith('M '))

    def test_consent_is_explicit_and_persistent(self):
        self.home()
        self.assertEqual(self.page.locator('.badge').inner_text(), 'AUS')
        self.action('companion').click()
        self.assertTrue(self.page.locator('dialog').is_visible())
        self.action('cancel-dialog').click()
        self.assertEqual(self.page.locator('.badge').inner_text(), 'AUS')
        self.action('companion').click()
        self.page.keyboard.press('Escape')
        self.assertEqual(self.page.locator('.badge').inner_text(), 'AUS')
        self.enable()
        self.assertEqual(self.page.locator('.badge').inner_text(), 'EIN')
        self.action('stop').first.click()
        self.assertTrue(self.page.locator('.idle').is_visible())
        self.page.reload()
        self.home()
        self.assertEqual(self.page.locator('.badge').inner_text(), 'EIN')
        self.action('companion').click()
        self.page.reload()
        self.home()
        self.assertEqual(self.page.locator('.badge').inner_text(), 'AUS')

    def test_role_switch_keeps_journey_and_changes_context(self):
        self.home()
        labels = self.page.locator('.journey-node').all_text_contents()
        self.action('role-relative').click()
        self.assertIn('Annas Perspektive', self.page.locator('.intro').text_content())
        self.assertEqual(self.page.locator('.journey-node').all_text_contents(), labels)
        self.action('event-J02').click()
        expect(self.page.locator('article')).to_contain_text('Annas Perspektive')
        self.page.reload()
        self.home()
        self.assertEqual(self.action('role-relative').get_attribute('aria-pressed'), 'true')

    def test_zoom_window_panning_and_center(self):
        self.home()
        self.assertEqual(self.page.locator('.journey-node').count(), 8)
        self.action('center').click()
        self.assertIn('23.10.2026 bis 20.11.2026', self.page.locator('.journey-caption').inner_text())
        self.assertEqual(self.page.locator('.journey-node').count(), 10)
        self.action('next').click()
        self.assertIn('06.11.2026 bis 04.12.2026', self.page.locator('.journey-caption').inner_text())
        self.action('center').click()
        self.assertIn('23.10.2026 bis 20.11.2026', self.page.locator('.journey-caption').inner_text())
        self.action('zoom-in').click()
        self.assertTrue(self.page.locator('.journey-map.large').is_visible())
        self.action('zoom-out').click()
        self.action('zoom-out').click()
        self.assertEqual(self.page.locator('.journey-node').count(), 8)

    def test_placeholders_and_global_stop_from_every_view(self):
        self.home()
        for action in ['ask', 'exercises', 'reports', 'diary']:
            self.action(action).click()
            expect(self.page.locator('.placeholder')).to_be_visible()
            self.action('stop').click()
            self.assertTrue(self.page.locator('.idle').is_visible())
            self.home()
        self.action('settings').click()
        self.action('companion').click()
        self.page.locator('dialog [data-action="stop"]').click()
        self.assertFalse(self.page.locator('dialog').is_visible())
        self.assertTrue(self.page.locator('.idle').is_visible())
        self.home()
        self.assertEqual(self.page.locator('.badge').inner_text(), 'AUS')

    def test_settings_persistence_and_interview_reset(self):
        self.home()
        self.enable()
        self.action('role-relative').click()
        self.action('settings').click()
        self.page.select_option('#text-size', 'large')
        self.page.reload()
        self.home()
        self.assertEqual(self.page.locator('html').get_attribute('class'), 'large-text')
        self.action('settings').click()
        self.action('reset').click()
        self.action('cancel-dialog').click()
        self.assertIn('Aktive Begleitung: EIN', self.page.locator('main').inner_text())
        self.action('reset').click()
        self.action('confirm-reset').click()
        self.assertEqual(self.page.locator('.badge').inner_text(), 'AUS')
        self.assertEqual(self.action('role-patient').get_attribute('aria-pressed'), 'true')
        self.assertEqual(self.page.locator('html').get_attribute('class'), 'large-text')
        self.assertEqual(self.page.locator('.journey-node').count(), 8)

    def test_service_worker_and_offline_reload(self):
        self.page.wait_for_function('navigator.serviceWorker.controller !== null')
        self.page.wait_for_function("document.querySelector('#connection-status').textContent.includes('Offline bereit')")
        scope = self.page.evaluate('navigator.serviceWorker.ready.then(r => r.scope)')
        self.assertEqual(scope, self.url)
        manifest = self.page.evaluate("fetch('./manifest.webmanifest').then(r => r.json())")
        self.assertEqual(manifest['display'], 'standalone')
        self.assertEqual(manifest['start_url'], './')
        for icon in manifest['icons']:
            self.assertTrue(self.page.evaluate('(path) => fetch(path).then(r => r.ok)', icon['src']))
        self.home()
        self.enable()
        self.context.set_offline(True)
        self.page.reload()
        self.home()
        self.assertEqual(self.page.locator('.badge').inner_text(), 'EIN')
        self.action('event-J02').click()
        expect(self.page.locator('h1')).to_have_text('Operation')

    def test_storage_denied_and_corrupt_data(self):
        self.context.add_init_script("Storage.prototype.setItem = () => { throw new Error('storage denied'); };")
        self.page.reload()
        self.home()
        self.enable()
        self.assertTrue(self.page.locator('#storage-warning').is_visible())
        self.assertEqual(self.page.locator('.badge').inner_text(), 'EIN')
        with self.browser.new_context() as context:
            page = context.new_page()
            page.add_init_script("localStorage.setItem('smartcoach.preferences.v1', '{broken');")
            page.goto(self.url)
            page.locator('[data-action="home"]').click()
            self.assertEqual(page.locator('.badge').inner_text(), 'AUS')

    def test_root_hosting_and_app_shell_only_cache(self):
        handler = functools.partial(QuietHandler, directory=str(ROOT))
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with self.browser.new_context() as context:
                page = context.new_page()
                url = f'http://127.0.0.1:{server.server_port}/'
                page.goto(url)
                page.wait_for_function('navigator.serviceWorker.controller !== null')
                self.assertEqual(page.evaluate('navigator.serviceWorker.ready.then(r => r.scope)'), url)
                page.evaluate("fetch('./SMARTcoach_Spezifikation_v0.2.1.md').then(r => r.text())")
                cached = page.evaluate('caches.keys().then(async names => (await Promise.all(names.map(async n => (await (await caches.open(n)).keys()).map(r => r.url)))).flat())')
                self.assertFalse(any('.md' in item for item in cached))
                context.set_offline(True)
                page.reload()
                page.locator('[data-action="home"]').click()
                expect(page.locator('.journey-nodes')).to_be_visible()
        finally:
            server.shutdown()
            server.server_close()

    def test_responsive_layouts_touch_targets_and_keyboard(self):
        self.home()
        for width, height in [(1280, 800), (800, 1280), (600, 960), (360, 800)]:
            for large in [False, True]:
                self.page.set_viewport_size({'width': width, 'height': height})
                self.page.evaluate('(large) => document.documentElement.classList.toggle("large-text", large)', large)
                self.page.wait_for_timeout(100)
                self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Overflow {width}, large={large}')
                self.assertTrue(self.page.locator('.companion').is_visible())
                self.assertEqual(self.page.locator('.journey-node').count(), 8)
                small = self.page.locator('button:visible').evaluate_all('(buttons) => buttons.filter(b => b.getBoundingClientRect().height < 48 || b.getBoundingClientRect().width < 48).map(b => b.textContent)')
                self.assertEqual(small, [], f'Small targets {width}')
        self.page.set_viewport_size({'width': 1280, 'height': 800})
        self.action('companion').focus()
        self.page.keyboard.press('Enter')
        self.assertTrue(self.page.locator('dialog').is_visible())
        for _ in range(8):
            self.page.keyboard.press('Tab')
            self.assertTrue(self.page.evaluate('document.querySelector("dialog").contains(document.activeElement)'))
        self.page.keyboard.press('Escape')
        self.assertEqual(self.page.locator(':focus').get_attribute('data-action'), 'companion')

    def test_stop_pauses_media_and_cancels_speech(self):
        self.home()
        self.page.evaluate('''() => {
          window.testMedia = document.createElement('video');
          window.testMedia.dataset.paused = 'false';
          window.testMedia.pause = function () { this.dataset.paused = 'true'; };
          document.querySelector('main').append(window.testMedia);
          window.speechCancelled = false;
          speechSynthesis.cancel = () => { window.speechCancelled = true; };
        }''')
        self.action('stop').first.click()
        self.assertEqual(self.page.evaluate('window.testMedia.dataset.paused'), 'true')
        self.assertEqual(self.page.evaluate('window.testMedia.currentTime'), 0)
        self.assertTrue(self.page.evaluate('window.speechCancelled'))

    def test_skip_link_and_browser_back(self):
        self.home()
        self.page.locator('.skip-link').focus()
        self.page.keyboard.press('Enter')
        self.assertEqual(self.page.locator(':focus').get_attribute('id'), 'content')
        self.assertTrue(self.page.locator('.journey-nodes').is_visible())
        self.action('reports').click()
        expect(self.page.locator('.placeholder')).to_be_visible()
        self.page.go_back()
        expect(self.page.locator('.journey-nodes')).to_be_visible()

    def test_installability_in_normal_browser_profile(self):
        executable = os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
        with tempfile.TemporaryDirectory(prefix='smartcoach-browser-') as profile:
            context = self.playwright.chromium.launch_persistent_context(
                profile, executable_path=executable, headless=True, args=['--no-sandbox'])
            try:
                page = context.pages[0]
                page.goto(self.url)
                page.wait_for_function('navigator.serviceWorker.controller !== null')
                session = context.new_cdp_session(page)
                self.assertEqual(session.send('Page.getAppManifest')['errors'], [])
                self.assertEqual(session.send('Page.getInstallabilityErrors')['installabilityErrors'], [])
            finally:
                context.close()


if __name__ == '__main__':
    unittest.main()
