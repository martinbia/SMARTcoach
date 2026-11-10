"""Functional browser checks, served at the GitHub Pages repository subpath.

Run: python3 -m unittest discover -s tests -v
Requires Playwright and Chromium (see README). No application build required.
"""
import functools
import io
import json
import math
import os
from pathlib import Path
import shutil
import struct
import threading
import tempfile
import unittest
import wave
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright, expect
from video_fixture import VIDEO

ROOT = Path(__file__).resolve().parents[1]


def wav_fixture(phase=0, duration=3):
    output = io.BytesIO()
    with wave.open(output, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(8000)
        samples = [int(9000 * math.sin(2 * math.pi * 440 * index / 8000 + phase)) for index in range(int(8000 * duration))]
        wav.writeframes(struct.pack('<' + 'h' * len(samples), *samples))
    return output.getvalue()


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
            while self.action('dialogue-next').count() and self.action('dialogue-next').is_enabled():
                self.action('dialogue-next').click()

    def expect_function_view(self, action):
        selectors = {'ask': '.dialogue-demo', 'exercises': '.video-catalog', 'reports': '.content-list', 'diary': '.entry-card'}
        expect(self.page.locator(selectors[action]).first).to_be_visible()

    def import_prompt_wavs(self, dialogue_ids):
        for identifier in dialogue_ids:
            self.page.locator(f'#prompt-wav-{identifier}').set_input_files({
                'name': f'{identifier}.wav', 'mimeType': 'application/octet-stream', 'buffer': wav_fixture(duration=0.12)
            })
            expect(self.page.locator(f'#prompt-audio-status-{identifier}')).to_have_text('Gespeichert')

    def accelerate_idle_timer(self):
        self.page.evaluate('''() => {
          const original = window.setTimeout.bind(window);
          window.setTimeout = (callback, delay, ...args) => original(callback, delay >= 5000 ? 10 : delay, ...args);
        }''')

    def mock_audio_completion(self):
        self.page.evaluate('''() => {
          HTMLMediaElement.prototype.pause = function() {};
          HTMLMediaElement.prototype.load = function() {};
          HTMLMediaElement.prototype.play = function() {
            window.automaticPlayAttempts = (window.automaticPlayAttempts || 0) + 1;
            return Promise.resolve();
          };
        }''')

    def finish_automatic_audio(self):
        self.page.evaluate("document.querySelector('#prompt-wav-player').dispatchEvent(new Event('ended'))")

    def configure_automatic_dialogues(self, wait_seconds=5):
        rows = {'A': ['A1', 'A2', 'A3'], 'B': ['B1'], 'C': ['C1', 'C2', 'C3', 'C4'], 'D': ['D1', 'D2', 'D3', 'D4', 'D5']}
        self.home()
        self.enable()
        self.action('settings').click()
        for identifier, steps in rows.items():
            self.page.select_option('#proactive-dialogue', identifier)
            self.import_prompt_wavs(steps)
        self.page.select_option('#proactive-dialogue', 'A')
        self.page.locator('#proactive-wait').fill(str(wait_seconds))
        self.page.locator('#proactive-wait').press('Tab')
        self.page.clock.install()
        return rows

    def start_idle_timer(self):
        self.action('home').first.click()
        self.action('stop').click()
        expect(self.page.locator('#idle-timer-progress')).to_be_visible()

    def test_idle_navigation_and_event_sources(self):
        self.assertTrue(self.page.locator('.idle').is_visible())
        self.home()
        for event, title in [('J02', 'Operation'), ('J05', 'Austritt'), ('J09', 'Heute')]:
            self.action(f'event-{event}').click()
            expect(self.page.locator('h1')).to_have_text(title)
            self.assertIn('Demo', self.page.locator('.event-source').inner_text())
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
        self.assertTrue(any(name.endswith(':v0.5.10') for name in self.page.evaluate('caches.keys()')))
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
        self.action('home').first.click()
        self.action('ask').click()
        self.assertTrue(self.page.locator('.automatic-coach-illustration img').evaluate(
            '(img) => img.complete && img.naturalWidth > 0'))

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
                self.assertEqual(sum('/content/' in item and '.md' in item for item in cached), 5)
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
            expect(self.page.locator('.event-source')).to_contain_text('E07')
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
        expect(self.page.locator('.event-source')).to_contain_text('E02')
        self.action('journey').click()
        expect(self.page.locator('.journey-caption')).to_contain_text('23.10.2026 bis 20.11.2026')
        self.action('role-relative').click()
        expect(self.page.locator('h1')).to_have_text('Meine Begleit-Woche')
        self.assertEqual(self.page.locator('.week-detail-item').count(), 6)
        self.action('week-A04').click()
        expect(self.page.locator('h1')).to_have_text('Belastung prüfen')
        self.action('journey').click()
        self.action('event-J10').click()
        expect(self.page.locator('.event-source')).to_contain_text('E07')
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

    def test_dialogue_calendar_progress_rewind_compact_controls_and_topic_return(self):
        self.home()
        self.demo_dialogue('D01')
        expect(self.page.locator('.dialogue-notice')).to_have_count(0)
        expect(self.page.locator('.dialogue-modes')).to_have_count(0)
        expect(self.page.locator('.dialogue-voice')).to_have_count(0)
        expect(self.action('dialogue-restart')).to_have_count(0)
        expect(self.action('dialogue-mode-text')).to_have_count(0)
        expect(self.action('dialogue-mode-voice')).to_have_count(0)
        expect(self.page.locator('.questions-nav')).to_have_count(0)
        expect(self.page.locator('.dialogue-session')).to_have_count(0)
        expect(self.action('dialogue-other-conversations')).to_have_count(0)
        expect(self.page.locator('.questions-topbar [data-action="home"]')).to_have_attribute('aria-label', 'Zurück zur Übersicht')
        expect(self.page.locator('.dialogue-log')).to_be_visible()
        self.assertGreater(self.page.locator('.dialogue-log').bounding_box()['height'], 300)
        expect(self.page.locator('.dialogue-message')).to_have_count(1)
        bubble = self.page.locator('.questions-manual-content .automatic-message-bubble').first
        font_size = bubble.evaluate('(node) => parseFloat(getComputedStyle(node).fontSize)')
        line_height = bubble.evaluate('(node) => { const style = getComputedStyle(node); return parseFloat(style.lineHeight) / parseFloat(style.fontSize); }')
        self.assertGreater(font_size, 20)
        self.assertGreaterEqual(line_height, 1.4)
        self.assertLessEqual(line_height, 1.5)
        expect(self.action('dialogue-previous')).to_be_disabled()
        self.action('dialogue-next').focus()
        self.page.keyboard.press('Enter')
        expect(self.page.locator('.dialogue-message')).to_have_count(2)
        self.action('dialogue-next').click()
        expect(self.page.locator('.dialogue-log')).to_contain_text('26. Januar 2027')
        expect(self.page.locator('.dialogue-log')).to_contain_text('25. Januar')
        self.action('dialogue-previous').click()
        expect(self.page.locator('.dialogue-message')).to_have_count(2)
        self.page.locator('.questions-topbar [data-action="home"]').click()
        expect(self.page.locator('.dashboard')).to_be_visible()
        self.action('ask').click()
        expect(self.page.locator('.dialogue-topics button')).to_have_count(3)
        self.action('dialogue-select-D01').click()
        expect(self.page.locator('.dialogue-progress')).to_have_text('Schritt 1 von 7')
        while self.action('dialogue-next').count() and self.action('dialogue-next').is_enabled():
            self.action('dialogue-next').click()
        expect(self.page.locator('.dialogue-complete-note')).to_have_text('Gespräch abgeschlossen.')
        expect(self.action('dialogue-next')).to_have_count(0)
        expect(self.action('dialogue-media')).to_have_count(0)
        self.assertTrue(self.page.locator('.dialogue-log').evaluate('(log) => log.scrollHeight > log.clientHeight'))
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        self.assertEqual(self.page.evaluate('SMART_DEMO.events.find(e => e.id === "J10").date'), '2026-11-10')
        self.assertEqual(self.action('dialogue-other-conversations').count(), 0)
        self.page.locator('.questions-topbar [data-action="home"]').click()
        self.action('ask').click()
        expect(self.page.locator('.dialogue-topics button')).to_have_count(3)

    def test_manual_chat_header_and_font_in_all_topics_and_tablet_sizes(self):
        def assert_header_clear():
            self.assertTrue(self.page.evaluate('''() => {
              const nodes = ['.brand', '.questions-back', '.role-switch', '.header-actions']
                .map(selector => document.querySelector(`.questions-topbar ${selector}`)?.getBoundingClientRect());
              if (nodes.some(node => !node)) return false;
              for (let i = 0; i < nodes.length; i++) for (let j = i + 1; j < nodes.length; j++) {
                const a = nodes[i], b = nodes[j];
                if (a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top) return false;
              }
              return document.querySelector('.questions-back').getBoundingClientRect().height >= 48;
            }'''))
        self.home()
        self.action('ask').click()
        expect(self.page.locator('.questions-topbar')).to_be_visible()
        expect(self.page.locator('.questions-topbar [data-action="home"]')).to_have_attribute('aria-label', 'Zurück zur Übersicht')
        expect(self.page.locator('.questions-nav')).to_have_count(0)
        assert_header_clear()
        for identifier in ('D01', 'D02', 'D03'):
            self.action(f'dialogue-select-{identifier}').click()
            expect(self.page.locator('.automatic-chat-heading h1')).to_have_text('Fragen stellen')
            expect(self.page.locator('.questions-manual-content .dialogue-session')).to_have_count(0)
            expect(self.action('dialogue-other-conversations')).to_have_count(0)
            bubble = self.page.locator('.questions-manual-content .automatic-message-bubble').first
            expect(bubble).to_be_visible()
            self.assertTrue(bubble.evaluate('''(node) => {
              const style = getComputedStyle(node);
              const size = parseFloat(style.fontSize);
              const lineHeight = parseFloat(style.lineHeight) / size;
              return size >= 21 && lineHeight >= 1.4 && lineHeight <= 1.5
                && style.overflowWrap === 'anywhere' && node.scrollWidth <= node.clientWidth;
            }'''))
            log = self.page.locator('.questions-manual-content .dialogue-log')
            self.assertGreater(log.bounding_box()['height'], 350)
            self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
            self.page.locator('.questions-topbar [data-action="home"]').click()
            expect(self.page.locator('.dashboard')).to_be_visible()
            self.action('ask').click()
        self.page.set_viewport_size({'width':800,'height':1280})
        self.action('dialogue-select-D03').click()
        expect(self.page.locator('.questions-topbar .questions-back-short')).to_be_visible()
        expect(self.page.locator('.questions-topbar .questions-back-full')).to_be_hidden()
        expect(self.page.locator('.questions-topbar [data-action="home"]')).to_have_attribute('aria-label', 'Zurück zur Übersicht')
        assert_header_clear()
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        self.page.locator('.questions-topbar [data-action="home"]').click()
        expect(self.page.locator('.dashboard')).to_be_visible()

    def test_questions_shared_layout_for_topics_manual_conversation_and_anna(self):
        def assert_layout(portrait=False):
            expect(self.page.locator('.questions-page')).to_be_visible()
            expect(self.page.locator('.automatic-coach-card')).to_be_visible()
            expect(self.page.locator('.automatic-chat-card')).to_be_visible()
            illustration = self.page.locator('.automatic-coach-illustration img')
            expect(illustration).to_have_attribute('src', './assets/coach-reference.png')
            self.assertTrue(illustration.evaluate('(img) => img.complete && img.naturalWidth > 0'))
            self.assertEqual(illustration.evaluate('(img) => [img.naturalWidth, img.naturalHeight]'), [312, 413])
            self.assertEqual(illustration.evaluate('(img) => getComputedStyle(img).objectFit'), 'contain')
            image_box = illustration.bounding_box()
            wrapper_box = self.page.locator('.automatic-coach-illustration').bounding_box()
            contained = illustration.evaluate('''(img) => {
              const box = img.getBoundingClientRect();
              const scale = Math.min(box.width / img.naturalWidth, box.height / img.naturalHeight);
              return [img.naturalWidth * scale, img.naturalHeight * scale];
            }''')
            self.assertLess(abs(contained[0] / contained[1] - 312 / 413), .01)
            self.assertGreaterEqual(image_box['y'], wrapper_box['y'] - 1)
            self.assertLessEqual(image_box['y'] + image_box['height'], wrapper_box['y'] + wrapper_box['height'] + 1)
            self.assertEqual(self.page.locator('.automatic-coach-caption').count(), 0)
            self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
            cols = self.page.evaluate('''() => getComputedStyle(document.querySelector('.questions-layout')).gridTemplateColumns.split(' ').map(parseFloat)''')
            self.assertEqual(len(cols), 1 if portrait else 2)
            if not portrait:
                self.assertLess(abs(cols[0] / sum(cols) - .38), .02)

        self.home()
        self.action('ask').click()
        assert_layout()
        expect(self.page.locator('.automatic-chat-heading')).to_contain_text('Wählen Sie ein Gesprächsthema')
        expect(self.page.locator('.dialogue-topics button')).to_have_count(3)
        self.assertEqual(self.page.locator('#automatic-dialogue-view').count(), 0)
        self.action('dialogue-select-D01').click()
        assert_layout()
        expect(self.page.locator('.automatic-chat-heading')).to_contain_text('Vorbereitetes Gespräch')
        expect(self.page.locator('.dialogue-log')).to_be_visible()
        self.action('dialogue-next').click()
        expect(self.page.locator('.dialogue-message')).to_have_count(2)
        self.assertTrue(self.action('dialogue-next').is_visible())
        expect(self.action('dialogue-other-conversations')).to_have_count(0)
        self.page.locator('.questions-topbar [data-action="home"]').click()
        expect(self.page.locator('.dashboard')).to_be_visible()
        self.action('ask').click()
        expect(self.page.locator('.dialogue-topics button')).to_have_count(3)
        self.page.set_viewport_size({'width':800,'height':1280})
        assert_layout(portrait=True)
        self.assertLessEqual(self.page.locator('.automatic-coach-card').bounding_box()['height'], 200)
        self.page.set_viewport_size({'width':1280,'height':800})
        self.action('home').click()
        self.action('role-relative').click()
        self.action('ask').click()
        expect(self.page.locator('.questions-topbar [data-action="home"]')).to_have_attribute('aria-label', 'Zurück zur Übersicht')
        assert_layout()
        expect(self.page.locator('.automatic-chat-heading')).to_contain_text('Für Anna sind noch keine Gespräche vorbereitet')
        expect(self.page.locator('.questions-empty-info')).to_contain_text('keine eigenen Gesprächsabläufe')
        self.assertEqual(self.page.locator('.dialogue-topics button').count(), 0)
        self.assertEqual(self.page.locator('#automatic-dialogue-view').count(), 0)

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

    def test_dialogue_d03_short_sequence_shows_image_action_and_returns(self):
        self.home()
        self.demo_dialogue('D03')
        log = self.page.locator('.dialogue-log')
        expect(log).to_contain_text('Ich möchte mein Röntgenbild anschauen. Können Sie es für mich suchen?')
        expect(log).not_to_contain_text('verheilt')
        expect(self.action('dialogue-media')).to_have_count(0)
        self.action('dialogue-next').click()
        expect(log).to_contain_text('Ja, gerne. Ich suche es in Ihrer Patientenakte auf EPIC.')
        self.action('dialogue-next').click()
        expect(self.page.locator('.dialogue-progress')).to_have_text('Schritt 3 von 3')
        expect(log).to_contain_text('Ich habe den Eintrag zum Röntgenbild gefunden. Soll ich Ihnen das Bild anzeigen?')
        expect(log.locator('.dialogue-message').nth(2).locator('strong')).to_have_text('SMARTcoach')
        expect(self.action('dialogue-next')).to_have_count(0)
        expect(self.action('dialogue-media')).to_have_text('Röntgenbild anzeigen')
        self.action('dialogue-media').click()
        expect(self.page.locator('#xray-view-status')).to_contain_text('einmalig in den Einstellungen auswählen')
        expect(self.page.locator('.xray-detail')).to_contain_text('keine Verbindung zu EPIC')
        self.page.locator('.xray-detail [data-action="ask"]').click()
        expect(self.page.locator('.dialogue-progress')).to_have_text('Schritt 3 von 3')
        expect(self.action('dialogue-media')).to_have_text('Röntgenbild anzeigen')

    def test_operation_and_journey_events_share_xray_and_readable_details(self):
        self.home()
        self.action('settings').click()
        self.page.locator('#xray-image').set_input_files({
            'name':'roentgen-demo.png','mimeType':'image/png',
            'buffer':(ROOT/'assets/icon-192.png').read_bytes()
        })
        expect(self.page.locator('#xray-status')).to_contain_text('lokal gespeichert')
        self.action('home').first.click()
        self.action('journey').click()
        self.page.locator('.journey-map [data-action="event-J02"]').click()
        expect(self.page.locator('.event-detail h1')).to_have_text('Operation')
        expect(self.page.locator('.event-description')).to_contain_text('Am 27. Oktober 2026 wurde der Bruch an Ihrer rechten Hüfte operiert.')
        expect(self.page.locator('.event-description')).to_contain_text('persönlichen Nachbehandlungsplan')
        expect(self.page.locator('.event-source')).to_contain_text('E02')
        expect(self.page.locator('.source')).to_have_count(0)
        self.assertGreaterEqual(float(self.page.locator('.event-description').evaluate('(node) => getComputedStyle(node).fontSize.replace("px", "")')), 21)
        self.assertLessEqual(float(self.page.locator('.event-source').evaluate('(node) => getComputedStyle(node).fontSize.replace("px", "")')), 12.1)
        expect(self.action('report-E02')).to_be_visible()
        expect(self.action('report-E03')).to_be_visible()
        expect(self.action('xray')).to_have_text('Röntgenbild ansehen')
        self.action('xray').click()
        self.page.wait_for_function('document.querySelector("#demo-xray")?.naturalWidth > 0')
        expect(self.page.locator('figcaption')).to_have_text('roentgen-demo.png')
        expect(self.page.locator('.xray-detail [data-action="event-J02"]')).to_have_text('← Zurück zur Operation')
        self.page.locator('.xray-detail [data-action="event-J02"]').click()
        expect(self.page.locator('.event-detail h1')).to_have_text('Operation')
        self.page.locator('.event-detail [data-action="journey"]').click()
        expect(self.page.locator('.journey-detail')).to_be_visible()
        self.page.locator('.journey-map [data-action="event-J10"]').click()
        expect(self.page.locator('.event-detail h1')).to_have_text('Physiotherapie')
        expect(self.page.locator('.event-detail .eyebrow')).to_contain_text('10.11.2026')
        expect(self.page.locator('.event-source')).to_be_visible()
        expect(self.page.locator('.source')).to_have_count(0)
        self.page.locator('.event-detail [data-action="journey"]').click()
        self.action('home').click()
        self.action('role-relative').click()
        self.action('journey').click()
        self.action('week-A01').click()
        expect(self.page.locator('.event-description')).to_be_visible()
        expect(self.page.locator('.event-source')).to_be_visible()
        expect(self.page.locator('.source')).to_have_count(0)

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
        expect(self.page.locator('.dialogue-log')).to_contain_text('Ich habe den Eintrag zum Röntgenbild gefunden.')
        self.action('dialogue-media').click()
        self.page.wait_for_function('document.querySelector("#demo-xray")?.naturalWidth > 0')
        expect(self.page.locator('.xray-detail')).to_contain_text('keine Verbindung zu EPIC')
        expect(self.page.locator('figcaption')).to_have_text('roentgen-demo.png')
        self.action('ask').click()
        expect(self.page.locator('.dialogue-progress')).to_have_text('Schritt 3 von 3')
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

    def test_proactive_dialog_catalog_settings_wait_range_and_generic_locks(self):
        self.home()
        self.action('settings').click()
        expect(self.page.locator('#proactive-dialogue')).to_be_visible()
        expect(self.page.locator('#proactive-dialogue')).to_have_value('none')
        expect(self.page.locator('#proactive-wait')).to_have_value('60')
        expected = {'A': 3, 'B': 1, 'C': 4, 'D': 5}
        for identifier, count in expected.items():
            self.page.select_option('#proactive-dialogue', identifier)
            expect(self.page.locator('.prompt-audio-row')).to_have_count(count)
            self.assertEqual(self.page.locator('.prompt-audio-row').first.get_attribute('data-step-id'), f'{identifier}1')
        d5 = self.page.locator('[data-step-id="D5"]')
        expect(d5.locator('h3')).to_have_text('D5 · SMARTcoach')
        expect(d5.locator('.prompt-audio-step')).to_contain_text('Bitte nehmen Sie Ibuprofen nur gemäss Ihrer ärztlichen Verordnung ein.')
        expect(d5.locator('.prompt-audio-actions button')).to_have_count(3)
        self.assertEqual(self.page.locator('#prompt-wav-D5').get_attribute('type'), 'file')
        self.assertIsNone(self.page.locator('#prompt-wav-D5').get_attribute('accept'))
        self.assertIsNone(self.page.locator('#prompt-wav-D5').get_attribute('capture'))
        self.assertTrue(self.page.evaluate("SMART_PROMPT_AUDIO.isAllowed('D5')"))
        self.assertFalse(self.page.evaluate("SMART_PROMPT_AUDIO.isAllowed('D6')"))
        expect(self.page.locator('#proactive-settings-title')).to_contain_text('Automatische Ansprache')
        expect(d5.locator('h3')).not_to_contain_text('GESPERRT')
        self.page.locator('#proactive-wait').fill('5')
        self.page.locator('#proactive-wait').press('Tab')
        expect(self.page.locator('#proactive-wait-status')).to_contain_text('gespeichert')
        self.page.locator('#proactive-wait').fill('3600')
        self.page.locator('#proactive-wait').press('Tab')
        self.page.locator('#proactive-wait').fill('4')
        self.page.locator('#proactive-wait').press('Tab')
        expect(self.page.locator('#proactive-wait')).to_have_value('3600')
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('smartcoach.preferences.v1')).waitSeconds"), 3600)
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('smartcoach.preferences.v1')).proactiveDialogue"), 'D')
        source = (ROOT/'content/ansprache-dialoge.md').read_text()
        malformed = source.replace('### D5 · SMARTcoach', '### D5 · UnbekannteRolle')
        with self.assertRaises(Exception):
            self.page.evaluate('(text) => SMART_CONTENT.parsePromptCatalog(text)', malformed)
        source = source.replace('## Dialog B – Spaziergang', '### A4 · Patient · GESPERRT\nEin gesperrter Erweiterungsschritt.\n\n## Dialog B – Spaziergang')
        source = source.replace('## Dialog D – Befinden und Schmerzen', '## Dialog E – Erweiterungsprüfung\n\n### E1 · SMARTcoach\nEin neuer Dialog ohne Änderung an der GUI-Logik.\n\n## Dialog D – Befinden und Schmerzen')
        self.page.reload()
        self.home()
        self.action('settings').click()
        expect(self.page.locator('#proactive-dialogue')).to_have_value('D')
        expect(self.page.locator('#proactive-wait')).to_have_value('3600')
        self.assertIn('beginnt die Wartezeit auf dem Ruhebildschirm', self.page.locator('.proactive-settings').inner_text())
        extended = self.page.evaluate('(source) => SMART_CONTENT.parsePromptCatalog(source)', source)
        self.page.evaluate('(catalogue) => { SMART_CONTENT.promptDialogues = catalogue; SMART_PROMPT_AUDIO.configure(catalogue); }', extended)
        self.page.select_option('#proactive-dialogue', 'none')
        expect(self.page.locator('#proactive-dialogue option[value="E"]')).to_have_count(1)
        self.page.select_option('#proactive-dialogue', 'E')
        expect(self.page.locator('.prompt-audio-row')).to_have_count(1)
        self.page.select_option('#proactive-dialogue', 'A')
        expect(self.page.locator('.prompt-audio-row')).to_have_count(4)
        expect(self.page.locator('[data-step-id="A4"] .prompt-audio-warning')).to_contain_text('redaktionellen Katalog gesperrt')
        self.assertEqual(self.page.locator('[data-step-id="A4"] .prompt-audio-actions').count(), 0)
        self.assertFalse(self.page.evaluate("SMART_PROMPT_AUDIO.isAllowed('A4')"))

    def test_d5_wav_assignment_preview_replace_remove_and_restart(self):
        original = wav_fixture()
        replacement = wav_fixture(phase=0.6)
        self.home()
        self.action('settings').click()
        self.page.select_option('#proactive-dialogue', 'D')
        expect(self.page.locator('.prompt-audio-row')).to_have_count(5)
        d5 = self.page.locator('[data-step-id="D5"]')
        expect(d5.locator('.prompt-audio-step')).to_contain_text('Danke für die Information.')
        expect(d5.locator('.prompt-audio-step')).to_contain_text('Ändern Sie die Dosierung nicht selbstständig.')
        expect(d5.locator('h3')).not_to_contain_text('GESPERRT')
        with self.page.expect_file_chooser() as chooser:
            self.action('prompt-wav-choose-D5').click()
        self.assertFalse(chooser.value.is_multiple())
        self.page.locator('#prompt-wav-D5').set_input_files({'name':'D5.wav','mimeType':'application/octet-stream','buffer':original})
        expect(self.page.locator('#prompt-audio-status-D5')).to_have_text('Gespeichert')
        expect(d5.locator('.media-filename')).to_have_text('D5.wav')
        self.action('prompt-wav-preview-D5').click()
        self.page.wait_for_function('document.querySelector("#prompt-wav-player")?.currentTime > 0')
        self.page.reload()
        self.home()
        self.action('settings').click()
        self.page.select_option('#proactive-dialogue', 'D')
        expect(self.page.locator('[data-step-id="D5"] .media-filename')).to_have_text('D5.wav')
        expect(self.page.locator('#prompt-audio-status-D5')).to_have_text('Gespeichert')
        self.page.locator('#prompt-wav-D5').set_input_files({'name':'D5-ersetzt.wav','mimeType':'audio/x-wav','buffer':replacement})
        expect(self.page.locator('[data-step-id="D5"] .media-filename')).to_have_text('D5-ersetzt.wav')
        self.action('prompt-wav-remove-D5').click()
        expect(self.page.locator('#prompt-audio-status-D5')).to_have_text('Nicht zugeordnet')
        self.assertIsNone(self.page.evaluate("SMART_PROMPT_AUDIO.get('D5').then(r=>r?.name || null)"))

    def test_automatic_timer_requires_consent_dialog_and_complete_audio(self):
        self.page.clock.install()
        self.home()
        self.action('stop').click()
        expect(self.page.locator('.idle')).to_be_visible()
        self.assertFalse(self.page.locator('#idle-timer-progress').is_visible())
        self.page.clock.fast_forward(60000)
        expect(self.page.locator('.idle')).to_be_visible()

        self.home()
        self.enable()
        self.action('settings').click()
        self.page.select_option('#proactive-dialogue', 'C')
        self.page.locator('#proactive-wait').fill('5')
        self.page.locator('#proactive-wait').press('Tab')
        expect(self.page.locator('#proactive-dialogue-readiness')).to_contain_text('WAV C1 fehlt')
        self.action('home').first.click()
        self.action('stop').click()
        self.page.wait_for_timeout(100)
        self.page.clock.fast_forward(60000)
        expect(self.page.locator('.idle')).to_be_visible()
        self.assertFalse(self.page.locator('#idle-timer-progress').is_visible())

        self.home()
        self.action('role-relative').click()
        self.action('stop').click()
        expect(self.page.locator('.idle')).to_be_visible()
        self.assertFalse(self.page.locator('#idle-timer-progress').is_visible())

    def test_automatic_timer_five_and_sixty_seconds_rerender_and_navigation_reset(self):
        self.configure_automatic_dialogues(wait_seconds=5)
        self.mock_audio_completion()
        self.start_idle_timer()
        self.page.clock.fast_forward(2000)
        # This uses the same rerender path as the idle animation control.
        self.page.evaluate("document.querySelector('[data-action=idle-toggle]').click()")
        self.page.clock.fast_forward(2500)
        expect(self.page.locator('.idle')).to_be_visible()
        self.page.clock.fast_forward(500)
        expect(self.page.locator('#automatic-dialogue-view')).to_have_attribute('data-step-id', 'A1')
        self.page.clock.fast_forward(60000)
        expect(self.page.locator('#automatic-dialogue-view')).to_have_attribute('data-step-id', 'A1')
        self.assertEqual(self.page.evaluate('window.automaticPlayAttempts'), 1)

        self.action('home').first.click()
        self.action('settings').click()
        self.page.locator('#proactive-wait').fill('60')
        self.page.locator('#proactive-wait').press('Tab')
        self.action('home').first.click()
        self.action('stop').click()
        expect(self.page.locator('#idle-timer-progress')).to_be_visible()
        self.page.clock.fast_forward(59000)
        expect(self.page.locator('.idle')).to_be_visible()
        self.page.clock.fast_forward(1000)
        expect(self.page.locator('#automatic-dialogue-view')).to_have_attribute('data-step-id', 'A1')

        self.action('home').first.click()
        self.page.clock.fast_forward(60000)
        expect(self.page.locator('.dashboard')).to_be_visible()
        self.action('stop').click()
        expect(self.page.locator('#idle-timer-progress')).to_be_visible()
        self.page.clock.fast_forward(59000)
        expect(self.page.locator('.idle')).to_be_visible()

    def test_automatic_timer_cancels_on_background_and_manual_navigation(self):
        self.configure_automatic_dialogues(wait_seconds=5)
        self.mock_audio_completion()
        self.start_idle_timer()
        self.page.clock.fast_forward(2000)
        self.page.locator('.idle-open').click()
        self.page.clock.fast_forward(60000)
        expect(self.page.locator('.dashboard')).to_be_visible()
        self.action('stop').click()
        expect(self.page.locator('#idle-timer-progress')).to_be_visible()
        self.page.clock.fast_forward(2000)
        self.page.evaluate('''() => {
          Object.defineProperty(document, 'hidden', { configurable:true, get:() => window.testDocumentHidden });
          window.testDocumentHidden = true;
          document.dispatchEvent(new Event('visibilitychange'));
        }''')
        self.page.clock.fast_forward(60000)
        expect(self.page.locator('.idle')).to_be_visible()
        self.page.evaluate('window.testDocumentHidden=false; document.dispatchEvent(new Event("visibilitychange"))')
        expect(self.page.locator('#idle-timer-progress')).to_be_visible()
        self.page.clock.fast_forward(4500)
        expect(self.page.locator('.idle')).to_be_visible()
        self.page.clock.fast_forward(500)
        expect(self.page.locator('#automatic-dialogue-view')).to_have_attribute('data-step-id', 'A1')

    def test_automatic_dialogues_a_to_d_follow_catalogue_and_patient_choices(self):
        rows = self.configure_automatic_dialogues(wait_seconds=5)
        self.mock_audio_completion()
        for dialogue_id, step_ids in rows.items():
            if dialogue_id != 'A':
                self.action('settings').click()
                self.page.select_option('#proactive-dialogue', dialogue_id)
                self.action('home').first.click()
                self.action('stop').click()
                expect(self.page.locator('#idle-timer-progress')).to_be_visible()
            else:
                self.start_idle_timer()
            self.page.clock.fast_forward(5000)
            conversation = self.page.evaluate('(id) => SMART_CONTENT.promptDialogues.find(item=>item.id===id)', dialogue_id)
            if dialogue_id == 'A':
                for width, height in ((1280, 800), (800, 1280)):
                    self.page.set_viewport_size({'width':width,'height':height})
                    self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
                    expect(self.page.locator('.automatic-coach-card')).to_be_visible()
                    expect(self.page.locator('.automatic-chat-heading')).to_be_visible()
                    self.assertTrue(self.page.evaluate('''() => {
                      const columns = getComputedStyle(document.querySelector('.questions-layout')).gridTemplateColumns.split(' ').map(parseFloat);
                      return innerHeight > innerWidth ? columns.length === 1 : columns.length === 2 && Math.abs(columns[0] / (columns[0] + columns[1]) - .38) < .02;
                    }'''))
                    self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
                    if width == 800:
                        self.assertLessEqual(self.page.locator('.automatic-coach-card').bounding_box()['height'], 200)
            for index, step_id in enumerate(step_ids):
                view = self.page.locator('#automatic-dialogue-view')
                expect(view).to_have_attribute('data-step-id', step_id)
                step = conversation['steps'][index]
                if step['speaker'] == 'Patient':
                    expect(view).to_have_attribute('data-state', 'awaiting-patient')
                    expect(self.page.locator('[data-action="automatic-answer"]')).to_have_text(step['text'])
                    self.assertGreaterEqual(self.page.locator('[data-action="automatic-answer"]').bounding_box()['height'], 48)
                    self.action('automatic-answer').click()
                    expect(view).to_have_attribute('data-state', 'patient-speaking')
                else:
                    expect(view).to_have_attribute('data-state', 'coach-speaking')
                expect(view.locator('.automatic-chat-log')).to_contain_text(step['text'])
                self.assertEqual(self.page.locator('.automatic-message-body').last.inner_text().splitlines()[-1], step['text'])
                self.assertTrue(self.page.evaluate('''() => {
                  const log = document.querySelector('.automatic-chat-log');
                  const bubble = document.querySelector('.automatic-message:last-child .automatic-message-bubble');
                  return document.documentElement.scrollWidth <= innerWidth
                    && log.scrollWidth <= log.clientWidth
                    && bubble.scrollWidth <= bubble.clientWidth
                    && Math.abs(log.scrollHeight - log.clientHeight - log.scrollTop) <= 2;
                }'''))
                self.assertTrue(self.page.locator('#prompt-wav-player').get_attribute('src').startswith('blob:'))
                self.finish_automatic_audio()
            expect(self.page.locator('#automatic-dialogue-view')).to_have_attribute('data-state', 'completed')
            expect(self.page.locator('.automatic-complete')).to_have_text('Gespräch abgeschlossen.')
            self.page.set_viewport_size({'width':1280,'height':800})
            if dialogue_id == 'A':
                self.action('automatic-restart').click()
                expect(self.page.locator('#automatic-dialogue-view')).to_have_attribute('data-step-id', 'A1')
                self.assertEqual(self.page.locator('.automatic-chat-log .automatic-message').count(), 1)
            self.action('home').first.click()

    def test_automatic_audio_blocked_requires_tap_and_stop_cancels_continuation(self):
        self.home()
        self.enable()
        self.action('settings').click()
        self.page.select_option('#proactive-dialogue', 'A')
        self.import_prompt_wavs(['A1', 'A2', 'A3'])
        self.page.locator('#proactive-wait').fill('5')
        self.page.locator('#proactive-wait').press('Tab')
        self.page.clock.install()
        self.page.evaluate('''() => {
          HTMLMediaElement.prototype.play = function() {
            window.automaticPlayAttempts = (window.automaticPlayAttempts || 0) + 1;
            if (window.automaticPlayAttempts === 1) return Promise.reject(new DOMException('gesture required', 'NotAllowedError'));
            return Promise.resolve();
          };
        }''')
        self.action('home').first.click()
        self.action('stop').click()
        expect(self.page.locator('#idle-timer-progress')).to_be_visible()
        self.page.clock.fast_forward(5000)
        expect(self.page.locator('#automatic-dialogue-view')).to_have_attribute('data-state', 'audio-blocked')
        expect(self.page.locator('.questions-topbar [data-action="home"]')).to_have_attribute('aria-label', 'Zurück zur Übersicht')
        expect(self.page.locator('[data-action="automatic-play"]')).to_have_text('Ton abspielen')
        self.assertEqual(self.page.evaluate('window.automaticPlayAttempts'), 1)
        self.action('automatic-play').click()
        expect(self.page.locator('#automatic-dialogue-view')).to_have_attribute('data-state', 'coach-speaking')
        self.assertEqual(self.page.evaluate('window.automaticPlayAttempts'), 2)
        self.action('stop').click()
        expect(self.page.locator('.idle')).to_be_visible()
        # Returning to idle starts a fresh five-second timer. Keep a margin
        # before its boundary so scheduler jitter cannot turn this cancellation
        # check into a second automatic-dialog start.
        self.page.clock.fast_forward(4500)
        expect(self.page.locator('.idle')).to_be_visible()

    def test_prompt_wav_assignment_preview_replace_remove_and_offline_restart(self):
        original = wav_fixture()
        replacement = wav_fixture(phase=0.4)
        self.home()
        self.action('settings').click()
        self.page.select_option('#proactive-dialogue', 'A')
        picker = self.page.locator('#prompt-wav-A1')
        self.assertEqual(picker.get_attribute('type'), 'file')
        self.assertIsNone(picker.get_attribute('accept'))
        self.assertIsNone(picker.get_attribute('capture'))
        with self.page.expect_file_chooser() as chooser:
            self.action('prompt-wav-choose-A1').click()
        self.assertFalse(chooser.value.is_multiple())
        self.page.locator('#prompt-wav-A1').set_input_files({'name':'A1.wav','mimeType':'application/octet-stream','buffer':original})
        expect(self.page.locator('#prompt-audio-status-A1')).to_have_text('Gespeichert')
        expect(self.page.locator('[data-step-id="A1"]')).to_contain_text('SMARTcoach')
        expect(self.page.locator('[data-step-id="A1"]')).to_contain_text('Grüezi. Haben Sie heute schon eiweisshaltige Speisen gegessen?')
        expect(self.page.locator('[data-step-id="A1"] .media-filename')).to_have_text('A1.wav')
        self.page.evaluate("window.wavPlayCount=0; const a=document.querySelector('#prompt-wav-player'); a.addEventListener('play',()=>window.wavPlayCount++);")
        self.action('prompt-wav-preview-A1').click()
        self.page.wait_for_function('window.wavPlayCount > 0')
        self.action('prompt-wav-preview-A1').click()
        self.assertTrue(self.page.evaluate("document.querySelector('#prompt-wav-player').paused"))
        self.action('prompt-wav-preview-A1').click()
        self.page.wait_for_function('document.querySelector("#prompt-wav-player")?.currentTime > 0')
        self.page.evaluate("window.wavPlayerBeforeSettingsLeave=document.querySelector('#prompt-wav-player')")
        self.action('home').first.click()
        self.assertTrue(self.page.evaluate('window.wavPlayerBeforeSettingsLeave.paused'))
        self.action('settings').click()
        self.page.select_option('#proactive-dialogue', 'A')
        self.page.locator('#prompt-wav-A1').set_input_files({'name':'A1-ersetzt.wav','mimeType':'audio/x-wav','buffer':replacement})
        expect(self.page.locator('[data-step-id="A1"] .media-filename')).to_have_text('A1-ersetzt.wav')
        expect(self.page.locator('#prompt-audio-status-A1')).to_have_text('Gespeichert')
        data = self.page.evaluate("SMART_PROMPT_AUDIO.get('A1').then(async r=>({name:r.name, bytes:new Uint8Array(await r.blob.arrayBuffer()).length, persistent:r.persistent}))")
        self.assertEqual(data, {'name':'A1-ersetzt.wav','bytes':len(replacement),'persistent':True})
        self.page.wait_for_function('navigator.serviceWorker.controller !== null')
        self.context.set_offline(True)
        self.page.reload()
        self.home()
        self.action('settings').click()
        self.page.select_option('#proactive-dialogue', 'A')
        expect(self.page.locator('[data-step-id="A1"] .media-filename')).to_have_text('A1-ersetzt.wav')
        expect(self.page.locator('#prompt-audio-status-A1')).to_have_text('Gespeichert')
        self.action('prompt-wav-preview-A1').click()
        self.page.wait_for_function('document.querySelector("#prompt-wav-player")?.currentTime > 0')
        self.page.evaluate("window.wavPlayerBeforeStop=document.querySelector('#prompt-wav-player')")
        self.action('stop').click()
        expect(self.page.locator('.idle')).to_be_visible()
        self.assertTrue(self.page.evaluate('window.wavPlayerBeforeStop.paused'))
        self.page.evaluate("window.localWavBeforeRemove=SMART_PROMPT_AUDIO.get('A1').then(r=>r.blob.size)")
        self.home()
        self.action('settings').click()
        self.page.select_option('#proactive-dialogue', 'A')
        self.action('prompt-wav-remove-A1').click()
        expect(self.page.locator('#prompt-audio-status-A1')).to_have_text('Nicht zugeordnet')
        self.assertIsNone(self.page.evaluate("SMART_PROMPT_AUDIO.get('A1').then(r=>r?.name || null)"))
        self.assertEqual(len(original), len(wav_fixture()))

    def test_prompt_wav_session_only_failure_and_invalid_audio(self):
        self.context.add_init_script('''(() => {
          const original = indexedDB.open.bind(indexedDB);
          indexedDB.open = (name, ...args) => {
            if (name === 'smartcoach-prompt-audio') throw new DOMException('blocked', 'SecurityError');
            return original(name, ...args);
          };
        })();''')
        self.page.reload()
        self.home()
        self.action('settings').click()
        self.page.select_option('#proactive-dialogue', 'B')
        self.page.locator('#prompt-wav-B1').set_input_files({'name':'B1.txt','mimeType':'application/octet-stream','buffer':wav_fixture()})
        expect(self.page.locator('#prompt-audio-status-B1')).to_contain_text('Nicht zugeordnet')
        expect(self.page.locator('#prompt-audio-storage-status')).to_contain_text('Bitte eine WAV-Datei')
        self.page.locator('#prompt-wav-B1').set_input_files({'name':'B1.wav','mimeType':'application/octet-stream','buffer':b'not a wav file'})
        expect(self.page.locator('#prompt-audio-storage-status')).to_contain_text('WAV-Datei konnte nicht verwendet werden')
        self.page.locator('#prompt-wav-B1').set_input_files({'name':'B1.wav','mimeType':'application/octet-stream','buffer':wav_fixture()})
        expect(self.page.locator('#prompt-audio-status-B1')).to_have_text('Nur für diese Sitzung')
        expect(self.page.locator('#prompt-audio-storage-status')).to_contain_text('nur für diese Sitzung')
        self.assertNotIn('Gespeichert', self.page.locator('#prompt-audio-status-B1').inner_text())

    def test_prompt_audio_settings_responsive_and_no_automatic_start(self):
        self.home()
        self.action('settings').click()
        self.page.select_option('#proactive-dialogue', 'C')
        for width, height in [(1280, 800), (800, 1280)]:
            self.page.set_viewport_size({'width':width,'height':height})
            self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
            for control in self.page.locator('.proactive-settings button, .proactive-settings select, .proactive-settings input:not(.prompt-audio-input)').all():
                self.assertGreaterEqual(control.bounding_box()['height'], 48)
        self.action('home').first.click()
        self.enable()
        self.action('stop').click()
        self.page.wait_for_timeout(150)
        expect(self.page.locator('.idle')).to_be_visible()
        self.assertFalse(self.page.locator('#prompt-wav-player').count())

    def test_manual_dialog_hides_voice_demo_and_global_stop_still_works(self):
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
        expect(self.action('dialogue-mode-text')).to_have_count(0)
        expect(self.action('dialogue-mode-voice')).to_have_count(0)
        expect(self.action('dialogue-read')).to_have_count(0)
        expect(self.page.locator('.dialogue-voice')).to_have_count(0)
        self.action('dialogue-next').click()
        calls = self.page.evaluate('voiceCalls.spoken')
        self.assertEqual(len(calls), 0)
        before = self.page.evaluate('voiceCalls.cancelled')
        self.action('stop').click()
        expect(self.page.locator('.idle')).to_be_visible()
        self.assertGreater(self.page.evaluate('voiceCalls.cancelled'), before)
        self.assertEqual(self.page.evaluate('voiceCalls.spoken.length'), 0)

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
        expect(self.action('dialogue-mode-voice')).to_have_count(0)
        expect(self.action('dialogue-read')).to_have_count(0)
        for width, height in [(1280,800),(800,1280),(360,800)]:
            self.page.set_viewport_size({'width':width,'height':height})
            for large in [False, True]:
                self.page.evaluate('(value) => document.documentElement.classList.toggle("large-text",value)', large)
                self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
                for button in self.page.locator('.dialogue-demo button:visible').all():
                    bounds = button.bounding_box()
                    self.assertGreaterEqual(bounds['width'],48)
                    self.assertGreaterEqual(bounds['height'],48)
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
