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
        self.action('companion-details').click()
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
        self.action('companion-details').click()
        self.assertTrue(self.page.locator('dialog').is_visible())
        self.action('cancel-dialog').click()
        self.assertEqual(self.page.locator('.badge').inner_text(), 'AUS')
        self.action('companion-details').click()
        self.page.keyboard.press('Escape')
        self.assertEqual(self.page.locator('.badge').inner_text(), 'AUS')
        self.enable()
        self.assertEqual(self.page.locator('.badge').inner_text(), 'EIN')
        self.action('stop').first.click()
        self.assertTrue(self.page.locator('.idle').is_visible())
        self.page.reload()
        self.home()
        self.assertEqual(self.page.locator('.badge').inner_text(), 'EIN')
        self.action('companion-details').click()
        expect(self.page.locator('#dialog-title')).to_have_text('Aktive Begleitung ist EIN')
        self.action('companion').click()
        self.page.reload()
        self.home()
        self.assertEqual(self.page.locator('.badge').inner_text(), 'AUS')

    def test_role_switch_keeps_journey_and_changes_context(self):
        self.home()
        labels = self.page.locator('.journey-node').all_text_contents()
        self.action('role-relative').click()
        expect(self.page.locator('.greeting')).to_have_text('Guten Tag, Anna.')
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
                overflow = self.page.evaluate('''() => ({
                  width: innerWidth, scroll: document.documentElement.scrollWidth,
                  elements: [...document.querySelectorAll('body *')]
                    .filter(e => e.getBoundingClientRect().right > innerWidth + 1)
                    .map(e => ({tag: e.tagName, class: e.getAttribute('class'),
                      right: e.getBoundingClientRect().right, text: e.textContent.slice(0, 80)}))
                })''')
                self.assertLessEqual(overflow['scroll'], overflow['width'], f'Overflow {width}, large={large}: {overflow}')
                self.assertTrue(self.page.locator('.companion').is_visible())
                self.assertEqual(self.page.locator('.journey-node').count(), 8)
                small = self.page.locator('button:visible').evaluate_all('(buttons) => buttons.filter(b => b.getBoundingClientRect().height < 48 || b.getBoundingClientRect().width < 48).map(b => b.textContent)')
                self.assertEqual(small, [], f'Small targets {width}')
        self.page.set_viewport_size({'width': 1280, 'height': 800})
        self.action('companion-details').focus()
        self.page.keyboard.press('Enter')
        self.assertTrue(self.page.locator('dialog').is_visible())
        for _ in range(8):
            self.page.keyboard.press('Tab')
            self.assertTrue(self.page.evaluate('document.querySelector("dialog").contains(document.activeElement)'))
        self.page.keyboard.press('Escape')
        self.assertEqual(self.page.locator(':focus').get_attribute('data-action'), 'companion-details')

    def test_header_wraps_with_large_text_and_wider_font_metrics(self):
        self.page.set_viewport_size({'width': 360, 'height': 800})
        self.home()
        self.page.evaluate('document.documentElement.classList.add("large-text")')
        # Small metric differences across runner fonts must not force this row
        # wider than its container. This reproduces the reported CI overflow.
        self.page.add_style_tag(content='.header-actions button { letter-spacing: 1px; }')
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        for action in ['settings', 'stop']:
            bounds = self.action(action).bounding_box()
            self.assertGreaterEqual(bounds['x'], 0)
            self.assertLessEqual(bounds['x'] + bounds['width'], 360)
            self.assertGreaterEqual(bounds['height'], 48)
        self.action('settings').click()
        expect(self.page.locator('h1')).to_have_text('Einstellungen')
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        self.action('stop').click()
        expect(self.page.locator('.idle')).to_be_visible()

    def test_compact_dashboard_c_fits_tablet_and_opens_all_tiles(self):
        self.home()
        tiles = self.page.locator('.function-tile')
        self.assertEqual(tiles.count(), 6)
        self.assertEqual(tiles.evaluate_all('(buttons) => buttons.map(b => b.dataset.action)'),
                         ['companion-details', 'event-J10', 'ask', 'exercises', 'reports', 'diary'])
        self.assertEqual(tiles.locator('svg').count(), 6)
        self.assertEqual(self.page.locator('.demo-bar, .intro, .side-stack').count(), 0)
        expect(self.page.locator('.footer')).to_contain_text('Fiktive Demo')
        for role in ['role-patient', 'role-relative']:
            self.action(role).click()
            self.assertTrue(self.page.evaluate('document.documentElement.scrollHeight <= innerHeight'), 'Dashboard scrolls at 1280×800')
            self.assertTrue(self.page.locator('.function-tile, .journey-card').evaluate_all(
                '(els) => els.every(e => { const r=e.getBoundingClientRect(); return r.top>=0 && r.bottom<=innerHeight; })'))
        self.action('event-J10').first.click()
        expect(self.page.locator('h1')).to_have_text('Physiotherapie')
        expect(self.page.locator('.source')).to_contain_text('E07')
        self.action('home').first.click()
        for action in ['ask', 'exercises', 'reports', 'diary']:
            self.action(action).click()
            expect(self.page.locator('.placeholder')).to_be_visible()
            self.action('home').first.click()

    def test_enabled_companion_details_cancel_stop_and_keyboard(self):
        self.home()
        self.enable()
        self.action('companion-details').click()
        self.action('cancel-dialog').click()
        expect(self.page.locator('.badge')).to_have_text('EIN')
        self.action('companion-details').focus()
        self.page.keyboard.press('Enter')
        self.page.locator('dialog [data-action="stop"]').click()
        expect(self.page.locator('.idle')).to_be_visible()
        self.home()
        expect(self.page.locator('.badge')).to_have_text('EIN')
        self.action('companion-details').click()
        self.page.locator('dialog [data-action="companion"]').click()
        expect(self.page.locator('dialog')).not_to_be_visible()
        expect(self.page.locator('.badge')).to_have_text('AUS')

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

    def import_idle_image(self):
        self.home()
        self.action('settings').click()
        self.page.locator('#idle-photo').set_input_files(ROOT / 'assets/icon-192.png')
        expect(self.page.locator('#image-status')).to_have_text('Ihr Foto ist auf diesem Gerät gespeichert.')

    def test_local_idle_photo_persists_offline_and_can_be_removed(self):
        self.import_idle_image()
        self.action('stop').click()
        expect(self.page.locator('.idle-photo')).to_be_visible()
        self.page.wait_for_function('navigator.serviceWorker.controller !== null')
        self.context.set_offline(True)
        self.page.reload()
        self.page.wait_for_function('document.querySelector(".idle-photo")?.naturalWidth > 0')
        self.assertTrue(self.page.locator('.idle-photo').get_attribute('src').startswith('blob:'))
        self.home()
        self.action('settings').click()
        self.action('reset').click()
        self.action('confirm-reset').click()
        self.action('stop').click()
        expect(self.page.locator('.idle-photo')).to_be_visible()
        self.home()
        self.action('settings').click()
        self.action('remove-photo').click()
        expect(self.page.locator('#image-status')).to_contain_text('entfernt')
        self.page.reload()
        self.assertEqual(self.page.locator('.idle-photo').count(), 0)

    def test_idle_fades_and_lightens_in_sync_and_can_pause(self):
        self.import_idle_image()
        self.action('stop').click()
        self.page.reload()
        self.page.locator('.idle-photo').wait_for()
        self.page.emulate_media(reduced_motion='no-preference')
        self.page.evaluate('''async () => {
          for (const animation of document.getAnimations()) {
            animation.pause(); animation.currentTime = 16000;
          }
          await new Promise(requestAnimationFrame);
        }''')
        self.assertEqual(self.page.locator('.idle-content').evaluate('(e) => getComputedStyle(e).opacity'), '0')
        self.assertAlmostEqual(float(self.page.locator('.idle-wash').evaluate('(e) => getComputedStyle(e).opacity')), .06, places=2)
        self.assertTrue(self.page.locator('.idle-photo').evaluate('(e) => e.getAnimations().length > 0'))
        self.action('idle-toggle').click()
        self.assertEqual(self.page.locator('.idle-content').evaluate('(e) => getComputedStyle(e).opacity'), '1')
        self.assertEqual(self.page.locator('.idle-photo').evaluate('(e) => e.getAnimations().length'), 0)
        self.page.reload()
        self.page.locator('.idle-photo').wait_for()
        expect(self.action('idle-toggle')).to_have_text('Animation starten')
        self.action('idle-toggle').click()
        self.page.emulate_media(reduced_motion='reduce')
        self.assertEqual(self.page.locator('.idle-photo').evaluate('(e) => e.getAnimations().length'), 0)
        self.assertEqual(self.page.locator('.idle-content').evaluate('(e) => getComputedStyle(e).opacity'), '1')
        self.home()
        self.assertEqual(self.page.locator('.idle-photo').count(), 0)

    def test_invalid_idle_photo_and_unavailable_image_storage(self):
        self.home()
        self.action('settings').click()
        self.page.locator('#idle-photo').set_input_files({'name': 'broken.jpg', 'mimeType': 'image/jpeg', 'buffer': b'not an image'})
        expect(self.page.locator('#image-status')).to_contain_text('konnte nicht geöffnet')
        self.assertEqual(self.page.locator('.idle-photo-preview').count(), 0)
        self.page.locator('#idle-photo').set_input_files({'name': 'large.png', 'mimeType': 'image/png', 'buffer': b'x' * (12 * 1024 * 1024 + 1)})
        expect(self.page.locator('#image-status')).to_contain_text('höchstens 12 MB')
        self.context.add_init_script("indexedDB.open = () => { throw new DOMException('blocked', 'SecurityError'); };")
        self.page.reload()
        self.home()
        self.action('settings').click()
        expect(self.page.locator('#image-status')).to_contain_text('nicht verfügbar')

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
