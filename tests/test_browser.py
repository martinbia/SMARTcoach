"""Functional browser checks, served at the GitHub Pages repository subpath.

Run: python3 -m unittest discover -s tests -v
Requires Playwright and Chromium (see README). No application build required.
"""
import functools
import json
import os
from pathlib import Path
import shutil
import threading
import tempfile
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright, expect
from video_fixture import VIDEO

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
        self.page.locator('.summary-nodes').wait_for()

    def video_settings(self):
        if not self.page.locator('.dashboard').count():
            self.action('home').first.click()
        self.action('settings').click()

    def import_test_video(self, name='GehenMitTeilbelastung_video_720p.mp4', mime='video/mp4'):
        self.video_settings()
        self.page.locator('#local-videos').set_input_files({'name': name, 'mimeType': mime, 'buffer': VIDEO})
        expect(self.page.locator('#video-import-status')).to_contain_text('1 Film(e) lokal gespeichert')
        self.action('exercises').click()

    def enable(self):
        self.action('companion-details').click()
        self.action('confirm-consent').click()

    def demo_dialogue(self, identifier, finish=False):
        self.action('ask').click()
        self.action(f'dialogue-select-{identifier}').click()
        self.action('dialogue-next').wait_for()
        if finish:
            while self.action('dialogue-next').is_enabled():
                self.action('dialogue-next').click()

    def expect_function_view(self, action):
        selectors = {'ask': '.dialogue-demo', 'exercises': '.video-catalog', 'reports': '.content-list', 'diary': '.entry-card'}
        expect(self.page.locator(selectors[action]).first).to_be_visible()

    def test_idle_navigation_and_event_sources(self):
        self.assertTrue(self.page.locator('.idle').is_visible())
        self.home()
        for event, title in [('J02', 'Operation'), ('J05', 'Austritt'), ('J09', 'Heute')]:
            self.action(f'event-{event}').click()
            expect(self.page.locator('h1')).to_have_text(title)
            self.assertIn('Demo', self.page.locator('.source').inner_text())
            self.action('home').first.click()
        self.assertTrue(self.page.locator('.journey-line path').get_attribute('d').startswith('M'))

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

    def test_person_switch_changes_journey_and_context(self):
        self.home()
        labels = self.page.locator('.journey-node').all_text_contents()
        self.action('role-relative').click()
        expect(self.page.locator('.person-profile h1')).to_have_text('Anna')
        self.assertNotEqual(self.page.locator('.journey-node').all_text_contents(), labels)
        self.action('event-J10').click()
        expect(self.page.locator('article')).to_contain_text('Annas Perspektive')
        self.page.reload()
        self.home()
        self.assertEqual(self.action('role-relative').get_attribute('aria-pressed'), 'true')

    def test_zoom_window_panning_and_center(self):
        self.home()
        self.assertEqual(self.page.locator('.journey-node').count(), 8)
        self.action('journey').click()
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
            self.expect_function_view(action)
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
        self.enable()
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
        self.action('home').first.click()
        self.action('role-relative').click()
        expect(self.page.locator('#summary-title')).to_have_text('Meine Begleit-Woche')
        expect(self.page.locator('.badge')).to_have_text('AUS')
        self.page.wait_for_function('document.querySelector(".avatar").naturalWidth > 0')
        self.action('journey').click()
        expect(self.page.locator('.week-detail-list')).to_be_visible()

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
                self.assertFalse(any('SMARTcoach_Spezifikation' in item for item in cached))
                self.assertEqual(sum('/content/' in item and '.md' in item for item in cached), 4)
                context.set_offline(True)
                page.reload()
                page.locator('[data-action="home"]').click()
                expect(page.locator('.summary-nodes')).to_be_visible()
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

    def test_role_dashboards_fit_tablet_and_open_all_functions(self):
        self.home()
        for role in ['role-patient', 'role-relative']:
            self.action(role).click()
            tiles = self.page.locator('.function-tile')
            self.assertEqual(tiles.count(), 4)
            self.assertEqual(tiles.evaluate_all('(buttons) => buttons.map(b => b.dataset.action)'),
                             ['ask', 'exercises', 'reports', 'diary'])
            self.assertEqual(tiles.locator('svg').count(), 4)
            expect(self.page.locator('.footer')).to_contain_text('Fiktive Demo')
            self.assertTrue(self.page.evaluate('document.documentElement.scrollHeight <= innerHeight'), 'Dashboard scrolls at 1280×800')
            self.assertTrue(self.page.locator('.function-tile, .summary-journey, .companion-bar').evaluate_all(
                '(els) => els.every(e => { const r=e.getBoundingClientRect(); return r.top>=0 && r.bottom<=innerHeight; })'))
            self.action('event-J10').first.click()
            expect(self.page.locator('h1')).to_have_text('Physiotherapie')
            expect(self.page.locator('.source')).to_contain_text('E07')
            self.action('home').first.click()
            for action in ['ask', 'exercises', 'reports', 'diary']:
                self.action(action).click()
                self.expect_function_view(action)
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

    def test_companion_consent_is_separate_for_each_person(self):
        self.home()
        self.enable()
        self.action('role-relative').click()
        expect(self.page.locator('.badge')).to_have_text('AUS')
        self.action('companion-details').click()
        expect(self.page.locator('#dialog-body')).to_contain_text('Diese Einstellung gilt für Anna')
        self.action('confirm-consent').click()
        self.action('role-patient').click()
        expect(self.page.locator('.badge')).to_have_text('EIN')
        self.action('companion-details').click()
        self.action('companion').click()
        expect(self.page.locator('.badge')).to_have_text('AUS')
        self.action('role-relative').click()
        expect(self.page.locator('.badge')).to_have_text('EIN')
        self.page.reload()
        self.home()
        expect(self.page.locator('.person-profile h1')).to_have_text('Anna')
        expect(self.page.locator('.badge')).to_have_text('EIN')
        self.action('role-patient').click()
        expect(self.page.locator('.badge')).to_have_text('AUS')

    def test_legacy_consent_migrates_only_to_previously_selected_person(self):
        for old_role in ['patient', 'relative']:
            with self.browser.new_context() as context:
                page = context.new_page()
                payload = json.dumps({'role': old_role, 'active': True, 'textSize': 'normal'})
                page.add_init_script("localStorage.setItem('smartcoach.preferences.v1', " + json.dumps(payload) + ");")
                page.goto(self.url)
                page.locator('[data-action="home"]').click()
                expect(page.locator('.badge')).to_have_text('EIN')
                other_role = 'relative' if old_role == 'patient' else 'patient'
                page.locator(f'[data-action="role-{other_role}"]').click()
                expect(page.locator('.badge')).to_have_text('AUS')
                saved = page.evaluate("JSON.parse(localStorage.getItem('smartcoach.preferences.v1'))")
                self.assertTrue(saved['activeByRole'][old_role])
                self.assertFalse(saved['activeByRole'][other_role])

    def test_detailed_journeys_preserve_events_and_weekly_tasks(self):
        self.home()
        self.action('journey').click()
        expect(self.page.locator('h1')).to_have_text('Ernsts detaillierter Weg')
        self.assertEqual(self.page.locator('.all-events button').count(), 14)
        self.action('center').click()
        self.action('event-J02').first.click()
        expect(self.page.locator('.source')).to_contain_text('E02')
        self.action('journey').click()
        expect(self.page.locator('.journey-caption')).to_contain_text('23.10.2026 bis 20.11.2026')
        self.action('role-relative').click()
        expect(self.page.locator('h1')).to_have_text('Meine Begleit-Woche')
        self.assertEqual(self.page.locator('.week-detail-item').count(), 6)
        self.action('week-A04').click()
        expect(self.page.locator('h1')).to_have_text('Belastung prüfen')
        self.action('journey').click()
        self.action('event-J10').click()
        expect(self.page.locator('.source')).to_contain_text('E07')
        expect(self.page.locator('article')).to_contain_text('10.11.2026')
        self.action('stop').click()
        expect(self.page.locator('.idle')).to_be_visible()

    def test_anna_layout_and_honest_demo_content(self):
        self.home()
        self.action('role-relative').click()
        self.assertEqual(self.page.locator('.summary-nodes .journey-node').count(), 6)
        expect(self.page.locator('#summary-title')).to_have_text('Meine Begleit-Woche')
        expect(self.page.locator('.tile-exercises')).to_contain_text('Anleitungen')
        expect(self.page.locator('.tile-diary')).to_contain_text('Begleitweg')
        self.assertEqual(self.page.locator('input[type=checkbox]').count(), 0)
        expect(self.page.locator('.appointments-card')).to_contain_text('10.11.2026')
        self.assertNotIn('14:00', self.page.locator('.appointments-card').inner_text())
        for width, height in [(1280, 800), (800, 1280), (600, 960), (360, 800)]:
            for large in [False, True]:
                self.page.set_viewport_size({'width': width, 'height': height})
                self.page.evaluate('(large) => document.documentElement.classList.toggle("large-text", large)', large)
                self.page.wait_for_timeout(100)
                self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Anna overflow {width}, large={large}')
                small = self.page.locator('button:visible').evaluate_all('(buttons) => buttons.filter(b => b.getBoundingClientRect().height < 48 || b.getBoundingClientRect().width < 48).map(b => b.textContent)')
                self.assertEqual(small, [])

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
        self.assertTrue(self.page.locator('.summary-nodes').is_visible())
        self.action('reports').click()
        expect(self.page.locator('.content-list')).to_be_visible()
        self.page.go_back()
        expect(self.page.locator('.summary-nodes')).to_be_visible()

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

    def test_markdown_reports_and_entries_are_linked_to_journey(self):
        self.home()
        self.action('reports').click()
        expect(self.page.locator('.content-choice')).to_have_count(8)
        self.action('report-E02').click()
        expect(self.page.locator('main')).to_contain_text('Nagel im Innern des Knochens')
        self.assertEqual(self.page.locator('.report-section').count(), 4)
        self.action('event-J02').click()
        expect(self.page.locator('article')).to_contain_text('27.10.2026')
        self.action('home').first.click()
        self.action('diary').click()
        expect(self.page.locator('.entry-card')).to_have_count(3)
        expect(self.page.locator('main')).not_to_contain_text('Wenn Ernst nachts aufsteht')
        self.action('event-J06').first.click()
        expect(self.page.locator('.detail > article')).to_contain_text('03.11.2026')
        self.action('home').first.click()
        self.action('role-relative').click()
        self.action('diary').click()
        expect(self.page.locator('.entry-card')).to_have_count(2)
        expect(self.page.locator('main')).to_contain_text('Wenn Ernst nachts aufsteht')

    def test_video_catalogue_roles_and_missing_local_file(self):
        self.home()
        self.action('exercises').click()
        expect(self.page.locator('.video-row')).to_have_count(7)
        expect(self.page.get_by_role('table', name='Übungsvideos für Ernst')).to_be_visible()
        for width, height in [(1280, 800), (800, 1280)]:
            self.page.set_viewport_size({'width': width, 'height': height})
            last = self.page.locator('.video-row').last.bounding_box()
            self.assertLessEqual(last['y'] + last['height'], height, 'Alle sieben Filme sichtbar')
            for target in self.page.locator('.video-row button').all():
                bounds = target.bounding_box()
                self.assertGreaterEqual(bounds['height'], 48)
                self.assertGreaterEqual(bounds['width'], 48)
        self.action('video-V01').focus()
        self.page.keyboard.press('Enter')
        expect(self.page.locator('#video-status')).to_contain_text('noch nicht ausgewählt')
        self.assertTrue(self.action('play-video').is_disabled())
        self.assertIsNone(self.page.locator('video').get_attribute('src'))
        self.action('home').first.click()
        self.action('role-relative').click()
        self.action('exercises').click()
        expect(self.page.locator('h1')).to_have_text('Anleitungen')
        expect(self.page.locator('.video-row')).to_have_count(3)
        expect(self.page.locator('.video-catalog')).to_contain_text('Treppensteigen mit Krücken')
        expect(self.page.locator('.video-catalog')).not_to_contain_text('Kniebeugen')

    def test_local_video_real_playback_stop_and_offline_persistence(self):
        sent = []
        self.page.on('request', lambda request: sent.append(request.method) if request.method != 'GET' else None)
        self.home()
        self.import_test_video()
        self.action('video-V01').click()
        # Opening the chosen film starts playback without a second click.
        self.page.wait_for_function('document.querySelector("video")?.currentTime > 0')
        self.assertTrue(self.page.locator('video').get_attribute('src').startswith('blob:'))
        self.page.evaluate('window.testVideo = document.querySelector("video")')
        self.action('stop').click()
        self.assertTrue(self.page.evaluate('testVideo.paused'))
        self.assertEqual(self.page.evaluate('testVideo.currentTime'), 0)
        self.page.wait_for_function('navigator.serviceWorker.controller !== null')
        self.context.set_offline(True)
        self.page.reload()
        self.home()
        self.action('exercises').click()
        self.action('video-V01').click()
        self.page.wait_for_function('document.querySelector("video")?.currentTime > 0')
        self.video_settings()
        self.page.get_by_text('Einzelne Filme zuordnen oder ersetzen', exact=True).click()
        self.action('remove-video-V01').click()
        expect(self.page.locator('#video-import-status')).to_contain_text('entfernt')
        self.action('exercises').click()
        self.action('video-V01').click()
        expect(self.page.locator('#video-placeholder-message')).to_contain_text('noch nicht ausgewählt')
        self.assertEqual(sent, [])

    def test_android_generic_mime_duplicate_name_and_direct_selection(self):
        self.home()
        self.import_test_video('GehenMitTeilbelastung_video_720p (1).mp4', 'application/octet-stream')
        self.action('video-V01').click()
        self.page.wait_for_function('document.querySelector("video")?.currentTime > 0')
        self.video_settings()
        self.page.get_by_text('Einzelne Filme zuordnen oder ersetzen', exact=True).click()
        self.page.locator('#local-video-V01').set_input_files({'name': 'mein_lokaler_film.mp4', 'mimeType': 'application/octet-stream', 'buffer': VIDEO})
        expect(self.page.locator('#video-import-status')).to_contain_text('Film lokal gespeichert')
        self.action('exercises').click()
        self.action('video-V01').click()
        expect(self.page.locator('#selected-video-file')).to_contain_text('mein_lokaler_film.mp4')
        self.page.wait_for_function('document.querySelector("video")?.currentTime > 0')
        result = self.page.evaluate('''async () => {
          const value = await SMART_VIDEOS.access('read', 'V01');
          return { isFile: value.blob instanceof File, type: value.blob.type, size: value.blob.size, name: value.name };
        }''')
        self.assertFalse(result['isFile'])
        self.assertEqual(result['type'], 'video/mp4')
        self.assertEqual(result['size'], len(VIDEO))
        self.assertEqual(result['name'], 'mein_lokaler_film.mp4')

    def test_player_opened_during_import_becomes_ready_automatically(self):
        self.home()
        self.video_settings()
        self.page.evaluate('''() => {
          const original = SMART_VIDEOS.importFiles;
          SMART_VIDEOS.importFiles = async (...args) => {
            await new Promise(resolve => window.finishVideoImport = resolve);
            return original(...args);
          };
        }''')
        self.page.locator('#local-videos').set_input_files({'name': 'GehenMitTeilbelastung_video_720p.mp4', 'mimeType': 'video/mp4', 'buffer': VIDEO})
        self.action('exercises').click()
        self.action('video-V01').click()
        expect(self.page.locator('#video-placeholder-message')).to_contain_text('noch eingelesen')
        self.assertTrue(self.action('play-video').is_disabled())
        self.page.evaluate('finishVideoImport()')
        self.page.wait_for_function('document.querySelector("video")?.currentTime > 0')

    def test_navigation_during_direct_selection_recovers_player(self):
        self.home()
        self.video_settings()
        self.page.get_by_text('Einzelne Filme zuordnen oder ersetzen', exact=True).click()
        self.page.evaluate('''() => {
          const original = SMART_VIDEOS.choose;
          SMART_VIDEOS.choose = async (...args) => {
            await new Promise(resolve => window.finishVideoChoice = resolve);
            return original(...args);
          };
        }''')
        self.page.locator('#local-video-V01').set_input_files({'name': 'film.mp4', 'mimeType': 'video/mp4', 'buffer': VIDEO})
        self.action('stop').click()
        self.home()
        self.action('exercises').click()
        self.action('video-V01').click()
        expect(self.action('play-video')).to_be_disabled()
        self.page.evaluate('finishVideoChoice()')
        self.page.wait_for_function('document.querySelector("video")?.currentTime > 0')
        self.video_settings()
        expect(self.page.locator('#local-videos')).to_be_enabled()

    def test_video_plays_for_session_when_device_storage_rejects_writes(self):
        self.context.add_init_script('''(() => {
          const original = IDBDatabase.prototype.transaction;
          IDBDatabase.prototype.transaction = function (stores, mode, ...rest) {
            if (this.name === 'smartcoach-local-videos' && mode === 'readwrite')
              throw new DOMException('Test quota exceeded', 'QuotaExceededError');
            return original.call(this, stores, mode, ...rest);
          };
        })();''')
        self.page.reload()
        self.home()
        self.video_settings()
        self.page.locator('#local-videos').set_input_files({'name': 'GehenMitTeilbelastung_video_720p.mp4', 'mimeType': 'video/mp4', 'buffer': VIDEO})
        expect(self.page.locator('#video-import-status')).to_contain_text('nur für diese Sitzung')
        self.action('exercises').click()
        self.action('video-V01').click()
        expect(self.page.locator('#video-status')).to_contain_text('Bereit für diese Sitzung')
        self.page.wait_for_function('document.querySelector("video")?.currentTime > 0')
        self.action('stop').click()
        self.home()
        self.action('exercises').click()
        self.action('video-V01').click()
        self.page.wait_for_function('document.querySelector("video")?.currentTime > 0')

    def test_legacy_cached_file_and_recovery_after_broken_video(self):
        self.home()
        self.page.evaluate('''async bytes => {
          await SMART_VIDEOS.access('write', 'V01', new File([new Uint8Array(bytes)], 'alter_film.mp4', {type:'application/octet-stream'}));
        }''', list(VIDEO))
        self.action('exercises').click()
        self.action('video-V01').click()
        self.page.wait_for_function('document.querySelector("video")?.currentTime > 0')
        self.video_settings()
        self.page.get_by_text('Einzelne Filme zuordnen oder ersetzen', exact=True).click()
        self.page.locator('#local-video-V01').set_input_files({'name': 'defekte_datei.mp4', 'mimeType': 'video/mp4', 'buffer': b'not an MP4 file'})
        expect(self.page.locator('#video-import-status')).to_contain_text('Film lokal gespeichert')
        self.action('exercises').click()
        self.action('video-V01').click()
        expect(self.page.locator('#video-placeholder-message')).to_contain_text('nicht gelesen')
        expect(self.page.locator('#local-player')).not_to_be_visible()
        expect(self.action('play-video')).to_be_disabled()
        self.video_settings()
        self.page.get_by_text('Einzelne Filme zuordnen oder ersetzen', exact=True).click()
        self.page.locator('#local-video-V01').set_input_files({'name': 'wieder_lesbar.mp4', 'mimeType': 'video/mp4', 'buffer': VIDEO})
        expect(self.page.locator('#video-import-status')).to_contain_text('Film lokal gespeichert')
        self.action('exercises').click()
        self.action('video-V01').click()
        self.page.wait_for_function('document.querySelector("video")?.currentTime > 0')

    def test_video_view_fills_tablet_below_header_and_import_is_settings_only(self):
        self.home()
        self.import_test_video()
        for role in ['patient', 'relative']:
            self.action('home').first.click()
            self.action(f'role-{role}').click()
            self.action('exercises').click()
            self.assertEqual(self.page.locator('input[type=file]').count(), 0)
            self.action('video-V01').click()
            self.page.wait_for_function('document.querySelector("video")?.currentTime > 0')
            self.assertEqual(self.page.locator('input[type=file]').count(), 0)
            for width, height in [(1280, 800), (800, 1280), (360, 800)]:
                self.page.set_viewport_size({'width': width, 'height': height})
                for large in [False, True]:
                    self.page.evaluate('(large) => document.documentElement.classList.toggle("large-text", large)', large)
                    self.page.wait_for_function('''Math.abs(document.querySelector('.video-stage').getBoundingClientRect().height + document.querySelector('.video-header').getBoundingClientRect().height - innerHeight) < 2''')
                    rect = self.page.locator('#local-player').bounding_box()
                    header = self.page.locator('.video-header').bounding_box()
                    controls = self.page.locator('.video-controls').bounding_box()
                    self.assertAlmostEqual(rect['y'], header['height'], delta=2)
                    self.assertAlmostEqual(rect['width'], width, delta=2)
                    self.assertGreaterEqual(controls['y'], height - 2)
                    self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
                    for action in ['home', 'stop', 'role-patient', 'role-relative']:
                        target = self.action(action).bounding_box()
                        self.assertGreaterEqual(target['width'], 48)
                        self.assertGreaterEqual(target['height'], 48)
            self.page.set_viewport_size({'width': 1280, 'height': 800})
            self.page.evaluate('document.documentElement.classList.remove("large-text")')
            self.action('home').focus()
            self.page.keyboard.press('Enter')
            expect(self.page.locator('.dashboard')).to_be_visible()
            self.action('exercises').click()

    def test_all_seven_videos_import_in_settings_and_open_with_playback(self):
        self.home()
        self.video_settings()
        files = self.page.evaluate('SMART_CONTENT.videos.map(video => video.meta.Datei)')
        self.page.locator('#local-videos').set_input_files([
            {'name': name, 'mimeType': 'application/octet-stream', 'buffer': VIDEO} for name in files
        ])
        expect(self.page.locator('#video-import-status')).to_contain_text('7 Film(e) lokal gespeichert')
        self.action('exercises').click()
        for index in range(1, 8):
            row = self.page.locator('.video-row').nth(index - 1)
            if index % 3 == 1:
                row.locator('th').click()
            elif index % 3 == 2:
                row.locator('td').click(position={'x': 2, 'y': 2})
            else:
                self.action(f'video-V{index:02d}').click()
            self.page.wait_for_url(f'**/#video-V{index:02d}')
            self.page.wait_for_function('document.querySelector("video")?.currentTime > 0')
            self.assertEqual(self.page.locator('input[type=file]').count(), 0)
            self.action('exercises').click()
        self.action('home').first.click()
        self.action('role-relative').click()
        self.action('exercises').click()
        expect(self.page.locator('.video-row')).to_have_count(3)
        ids = self.page.locator('.video-row button').evaluate_all('(buttons) => buttons.map(button => button.dataset.action)')
        self.assertEqual(len(ids), 3)
        for index, action in enumerate(ids):
            self.page.locator('.video-row').nth(index).locator('th').tap()
            self.page.wait_for_url(f'**/#{action}')
            self.page.wait_for_function('document.querySelector("video")?.currentTime > 0')
            self.action('exercises').click()

    def test_blocked_automatic_video_start_keeps_manual_playback(self):
        self.home()
        self.import_test_video()
        self.page.evaluate('''() => {
          const original = HTMLMediaElement.prototype.play;
          HTMLMediaElement.prototype.play = function () {
            HTMLMediaElement.prototype.play = original;
            return Promise.reject(new DOMException('Test gesture required', 'NotAllowedError'));
          };
        }''')
        self.action('video-V01').click()
        expect(self.page.locator('#video-status')).to_contain_text('weiteren Tipp')
        expect(self.page.locator('video')).to_be_visible()
        expect(self.action('play-video')).to_be_enabled()
        self.action('play-video').click()
        self.page.wait_for_function('document.querySelector("video")?.currentTime > 0')
        self.page.locator('video').evaluate('(v) => v.pause()')
        self.action('play-video').click()
        self.page.wait_for_function('document.querySelector("video")?.currentTime > 0 && document.querySelector("video")?.currentTime < 1')
        self.action('stop').click()
        expect(self.page.locator('.idle')).to_be_visible()

    def test_dialogue_calendar_progress_rewind_restart_and_reset(self):
        self.home()
        self.demo_dialogue('D01')
        expect(self.page.locator('.dialogue-message')).to_have_count(1)
        expect(self.action('dialogue-previous')).to_be_disabled()
        self.action('dialogue-next').focus()
        self.page.keyboard.press('Enter')
        expect(self.page.locator('.dialogue-message')).to_have_count(2)
        self.action('dialogue-next').click()
        expect(self.page.locator('.dialogue-log')).to_contain_text('26. Januar 2027')
        expect(self.page.locator('.dialogue-log')).to_contain_text('25. Januar')
        self.action('dialogue-previous').click()
        expect(self.page.locator('.dialogue-message')).to_have_count(2)
        self.action('dialogue-restart').click()
        expect(self.page.locator('.dialogue-progress')).to_have_text('Schritt 1 von 7')
        while self.action('dialogue-next').is_enabled():
            self.action('dialogue-next').click()
        expect(self.action('dialogue-media')).to_have_text('Zurück zum Hauptmenü')
        self.assertEqual(self.page.evaluate('SMART_DEMO.events.find(e => e.id === "J10").date'), '2026-11-10')
        self.action('dialogue-media').click()
        expect(self.page.locator('.dashboard')).to_be_visible()
        self.action('ask').click()
        expect(self.page.locator('.dialogue-topics button')).to_have_count(3)

    def test_dialogue_exercise_video_plays_and_returns_to_main_menu(self):
        self.home()
        self.video_settings()
        self.page.locator('#local-videos').set_input_files({'name':'Wadenheber mit festhalten - beien gestreckt_video_720p.mp4','mimeType':'video/mp4','buffer':VIDEO})
        expect(self.page.locator('#video-import-status')).to_contain_text('1 Film(e) lokal gespeichert')
        self.action('home').first.click()
        self.demo_dialogue('D02', finish=True)
        self.action('dialogue-media').click()
        self.page.wait_for_url('**/#video-V07')
        self.page.wait_for_function('document.querySelector("video")?.currentTime > 0')
        self.page.wait_for_url('**/#home')
        expect(self.page.locator('.dashboard.role-patient')).to_be_visible()

    def test_dialogue_missing_media_can_be_stopped(self):
        self.home()
        self.demo_dialogue('D02', finish=True)
        self.action('dialogue-media').click()
        expect(self.page.locator('#video-placeholder-message')).to_contain_text('noch nicht ausgewählt')
        self.action('stop').click()
        expect(self.page.locator('.idle')).to_be_visible()
        self.home()
        self.demo_dialogue('D03', finish=True)
        self.action('dialogue-media').click()
        expect(self.page.locator('#xray-view-status')).to_contain_text('noch kein Bild')
        self.action('stop').click()
        expect(self.page.locator('.idle')).to_be_visible()

    def test_dialogue_xray_local_selection_offline_reset_and_removal(self):
        uploads = []
        self.page.on('request', lambda request: uploads.append(request.url) if request.method != 'GET' else None)
        self.home()
        self.action('settings').click()
        self.page.locator('#xray-image').set_input_files({'name':'roentgen-demo.png','mimeType':'application/octet-stream','buffer':(ROOT/'assets/icon-192.png').read_bytes()})
        expect(self.page.locator('#xray-status')).to_contain_text('lokal gespeichert')
        self.action('reset').click()
        self.action('confirm-reset').click()
        self.demo_dialogue('D03', finish=True)
        expect(self.page.locator('.dialogue-log')).to_contain_text('simuliert')
        self.action('dialogue-media').click()
        self.page.wait_for_function('document.querySelector("#demo-xray")?.naturalWidth > 0')
        expect(self.page.locator('.xray-detail')).to_contain_text('keine Verbindung zu EPIC')
        expect(self.page.locator('figcaption')).to_have_text('roentgen-demo.png')
        self.action('ask').click()
        expect(self.page.locator('.dialogue-progress')).to_have_text('Schritt 6 von 6')
        self.page.wait_for_function('navigator.serviceWorker.controller !== null')
        self.context.set_offline(True)
        self.page.reload()
        self.home()
        self.demo_dialogue('D03', finish=True)
        self.action('dialogue-media').click()
        self.page.wait_for_function('document.querySelector("#demo-xray")?.naturalWidth > 0')
        self.action('settings').first.click()
        self.action('remove-xray').click()
        expect(self.page.locator('#xray-status')).to_contain_text('Originaldatei bleibt erhalten')
        self.action('home').first.click()
        self.demo_dialogue('D03', finish=True)
        self.action('dialogue-media').click()
        expect(self.page.locator('#xray-view-status')).to_contain_text('noch kein Bild')
        self.assertEqual(uploads, [])

    def test_dialogue_xray_invalid_image_and_unavailable_storage(self):
        self.home()
        self.action('settings').click()
        self.page.locator('#xray-image').set_input_files({'name':'kaputt.png','mimeType':'image/png','buffer':b'not an image'})
        expect(self.page.locator('#xray-status')).to_contain_text('nicht gelesen')
        self.page.locator('#xray-image').set_input_files({'name':'falsches-format.dcm','mimeType':'application/dicom','buffer':b'dicom'})
        expect(self.page.locator('#xray-status')).to_contain_text('JPG, PNG oder WebP')
        self.context.add_init_script('''(() => {
          const original = indexedDB.open.bind(indexedDB);
          indexedDB.open = (name, ...args) => {
            if (name === 'smartcoach-demo-xray') throw new DOMException('Test blocked', 'SecurityError');
            return original(name, ...args);
          };
        })();''')
        self.page.reload()
        self.home()
        self.action('settings').click()
        self.page.locator('#xray-image').set_input_files(ROOT/'assets/icon-192.png')
        expect(self.page.locator('#xray-status')).to_contain_text('konnte nicht gespeichert')
        expect(self.page.locator('.xray-preview')).to_have_count(0)

    def test_dialogue_voice_uses_local_voice_and_global_stop(self):
        self.page.evaluate('''() => {
          window.voiceCalls = {spoken:[], cancelled:0};
          window.SpeechSynthesisUtterance = function (text) { this.text = text; };
          Object.defineProperty(window, 'speechSynthesis', {value:{
            getVoices:() => [{lang:'de-DE', localService:false, name:'remote'}, {lang:'de-CH', localService:true, name:'local'}],
            addEventListener:() => {}, cancel:() => {voiceCalls.cancelled++;},
            speak:utterance => voiceCalls.spoken.push({text:utterance.text, local:utterance.voice.localService})
          }});
        }''')
        self.home()
        self.demo_dialogue('D01')
        self.action('dialogue-mode-voice').click()
        expect(self.page.locator('.dialogue-voice')).to_contain_text('ohne Mikrofonaufnahme')
        self.action('dialogue-read').click()
        self.action('dialogue-next').click()
        self.action('dialogue-read').click()
        calls = self.page.evaluate('voiceCalls.spoken')
        self.assertEqual(len(calls), 2)
        self.assertTrue(all(call['local'] for call in calls))
        self.assertIn('Enkelkind', calls[0]['text'])
        self.assertIn('Beispielkalender', calls[1]['text'])
        before = self.page.evaluate('voiceCalls.cancelled')
        self.action('stop').click()
        expect(self.page.locator('.idle')).to_be_visible()
        self.assertGreater(self.page.evaluate('voiceCalls.cancelled'), before)
        self.assertEqual(self.page.evaluate('voiceCalls.spoken.length'), 2)

    def test_dialogue_markdown_changes_and_invalid_target(self):
        source = (ROOT/'content/dialoge.md').read_text()
        with self.browser.new_context(service_workers='block') as context:
            page = context.new_page()
            page.route('**/content/dialoge.md', lambda route: route.fulfill(body=source.replace('Beispielkalender für Januar 2027', 'REDIGIERTER BEISPIELKALENDER'), content_type='text/markdown'))
            page.goto(self.url)
            page.locator('[data-action="home"]').click()
            page.locator('[data-action="ask"]').click()
            page.locator('[data-action="dialogue-select-D01"]').click()
            page.locator('[data-action="dialogue-next"]').click()
            expect(page.locator('.dialogue-log')).to_contain_text('REDIGIERTER BEISPIELKALENDER')
            page.route('**/content/dialoge.md', lambda route: route.fulfill(body=source.replace('Aktion: video-V07', 'Aktion: video-V99'), content_type='text/markdown'))
            page.reload()
            page.locator('[data-action="home"]').click()
            expect(page.locator('main')).to_contain_text('Ungültiges Dialogziel')

    def test_dialogue_new_views_responsive_and_no_local_voice(self):
        self.home()
        self.demo_dialogue('D01', finish=True)
        self.action('dialogue-mode-voice').click()
        for width, height in [(1280,800),(800,1280),(360,800)]:
            self.page.set_viewport_size({'width':width,'height':height})
            for large in [False, True]:
                self.page.evaluate('(value) => document.documentElement.classList.toggle("large-text",value)', large)
                self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
                for button in self.page.locator('.dialogue-demo button:visible').all():
                    bounds = button.bounding_box()
                    self.assertGreaterEqual(bounds['width'],48)
                    self.assertGreaterEqual(bounds['height'],48)
        self.page.evaluate("Object.defineProperty(window.speechSynthesis, 'getVoices', {value:() => []})")
        self.action('dialogue-mode-voice').click()
        expect(self.action('dialogue-read')).to_be_disabled()
        expect(self.page.locator('#dialogue-voice-status')).to_contain_text('Keine lokale deutsche Stimme')
        self.action('home').first.click()
        self.action('settings').click()
        self.page.locator('#xray-image').set_input_files({'name':'sehr_langer_name_des_lokalen_demo_roentgenbildes.png','mimeType':'image/png','buffer':(ROOT/'assets/icon-192.png').read_bytes()})
        expect(self.page.locator('#xray-status')).to_contain_text('lokal gespeichert')
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Röntgen-Einstellung')
        self.action('home').first.click()
        self.demo_dialogue('D03', finish=True)
        self.action('dialogue-media').click()
        self.page.wait_for_function('document.querySelector("#demo-xray")?.naturalWidth > 0')
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Röntgenansicht')

    def test_markdown_edit_updates_date_everywhere_without_build(self):
        with self.browser.new_context(service_workers='block') as context:
            page = context.new_page()
            text = (ROOT / 'content/genesungsweg.md').read_text().replace('Datum: 2026-11-10', 'Datum: 2026-11-12')
            page.route('**/content/genesungsweg.md', lambda route: route.fulfill(body=text, content_type='text/markdown'))
            page.goto(self.url)
            page.locator('[data-action="home"]').click()
            expect(page.locator('.appointments-card')).to_contain_text('12.11.2026')
            page.locator('[data-action="reports"]').click()
            page.locator('[data-action="report-E07"]').click()
            expect(page.locator('.report-section').first).to_contain_text('12.11.2026')
            page.locator('[data-action="event-J05"]').click()
            page.locator('[data-action="home"]').first.click()
            expect(page.locator('[data-action="event-J10"]').first).to_contain_text('12.11.')

    def test_markdown_failure_and_html_are_not_silently_accepted(self):
        with self.browser.new_context(service_workers='block') as context:
            page = context.new_page()
            page.route('**/content/genesungsweg.md', lambda route: route.fulfill(body='# Incomplete file', content_type='text/markdown'))
            page.goto(self.url)
            page.locator('[data-action="home"]').click()
            expect(page.locator('h1')).to_have_text('Inhalte nicht verfügbar')
            expect(page.locator('[data-action="reload-content"]')).to_be_visible()
            page.unroute('**/content/genesungsweg.md')
            page.locator('[data-action="reload-content"]').click()
            expect(page.locator('.summary-nodes')).to_be_visible()
            html = page.evaluate('SMART_CONTENT.markdown("<img src=x onerror=alert(1)> **Text**")')
            self.assertIn('&lt;img', html)
            self.assertNotIn('<img', html)
            self.assertIn('<strong>Text</strong>', html)

    def test_new_content_views_do_not_overflow_small_screen(self):
        self.page.set_viewport_size({'width': 360, 'height': 800})
        self.home()
        for action in ['exercises', 'reports', 'diary']:
            self.action(action).click()
            self.expect_function_view(action)
            self.page.evaluate('document.documentElement.classList.add("large-text")')
            self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'), action)
            self.action('home').first.click()
        self.action('exercises').click()
        self.action('video-V01').click()
        self.video_settings()
        self.page.get_by_text('Einzelne Filme zuordnen oder ersetzen', exact=True).click()
        self.page.locator('#local-video-V01').set_input_files({'name': 'ein_sehr_langer_lokaler_filmname_auf_dem_Tablet.mp4', 'mimeType': 'video/mp4', 'buffer': VIDEO})
        expect(self.page.locator('#video-import-status')).to_contain_text('Film lokal gespeichert')
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Einstellungen-Dateiauswahl')
        self.action('exercises').click()
        self.action('video-V01').click()
        expect(self.action('play-video')).to_be_enabled()
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Video-Dateiauswahl')


if __name__ == '__main__':
    unittest.main()
