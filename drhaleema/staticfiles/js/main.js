// ── Hero tagline typing animation ────────────────────────────
(function () {
    const el = document.querySelector('.hero-tagline');
    if (!el) return;

    const segments = [
        { text: 'Chronic Disease Management', speed: 52 },
        { text: '  |  ',                       speed: 90 },
        { text: "Women’s Health",          speed: 52 },
        { text: '  |  ',                       speed: 90 },
        { text: 'Holistic Wellness',            speed: 52 },
    ];

    // Cursor element
    const cursor = document.createElement('span');
    cursor.className = 'typing-cursor';

    el.textContent = '';
    el.appendChild(cursor);

    let segIdx = 0, charIdx = 0, typed = '';

    function tick() {
        if (segIdx >= segments.length) return; // finished — cursor keeps blinking

        const seg = segments[segIdx];
        if (charIdx < seg.text.length) {
            typed += seg.text[charIdx];
            el.textContent = typed;
            el.appendChild(cursor);
            charIdx++;
            setTimeout(tick, seg.speed);
        } else {
            segIdx++;
            charIdx = 0;
            // Pause between phrases, shorter between separators
            setTimeout(tick, segIdx < segments.length ? 220 : 0);
        }
    }

    // Start after hero h1 + qualification have animated in (~750 ms)
    setTimeout(tick, 850);
}());

// CSRF token helper
function getCookie(name) {
    let val = null;
    document.cookie.split(';').forEach(c => {
        c = c.trim();
        if (c.startsWith(name + '=')) val = decodeURIComponent(c.slice(name.length + 1));
    });
    return val;
}

// ── Auto-dismiss alerts ─────────────────────────────────────
document.querySelectorAll('.alert').forEach(el => {
    setTimeout(() => {
        el.style.transition = 'opacity 0.4s';
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 400);
    }, 4000);
});

// ── Set minimum date on all date pickers to today ───────────
document.querySelectorAll('input[type="date"]').forEach(el => {
    if (!el.min) {
        const today = new Date().toISOString().split('T')[0];
        el.min = today;
    }
});

// ── Slot loader ─────────────────────────────────────────────
(function () {
    const dateInput    = document.getElementById('id_appointment_date');
    const timeSelect   = document.getElementById('id_appointment_time');
    const loadingMsg   = document.getElementById('slot-loading');
    const noSlotsMsg   = document.getElementById('no-slots-msg');

    if (!dateInput || !timeSelect) return;

    function getPatientType() {
        const radios = document.querySelectorAll('input[name="patient_type"]');
        for (const r of radios) {
            if (r.checked) return r.value;
        }
        return '';
    }

    function loadSlots() {
        const dateVal = dateInput.value;
        const ptVal   = getPatientType();

        if (!dateVal || !ptVal) return;

        const url = `/ajax/slots/?date=${encodeURIComponent(dateVal)}&patient_type=${encodeURIComponent(ptVal)}`;

        // Reset
        timeSelect.innerHTML = '<option value="">Loading...</option>';
        timeSelect.disabled = true;
        if (loadingMsg) loadingMsg.style.display = 'block';
        if (noSlotsMsg) noSlotsMsg.style.display = 'none';

        fetch(url)
            .then(r => r.json())
            .then(data => {
                if (loadingMsg) loadingMsg.style.display = 'none';
                timeSelect.innerHTML = '';

                if (!data.slots || data.slots.length === 0) {
                    timeSelect.innerHTML = '<option value="">No slots available</option>';
                    timeSelect.disabled = true;
                    if (noSlotsMsg) noSlotsMsg.style.display = 'block';
                    return;
                }

                const placeholder = document.createElement('option');
                placeholder.value = '';
                placeholder.textContent = '-- Select a time slot --';
                timeSelect.appendChild(placeholder);

                // Format 24h → 12h display
                data.slots.forEach(slot => {
                    const opt = document.createElement('option');
                    opt.value = slot;
                    const [hh, mm] = slot.split(':').map(Number);
                    const ampm = hh < 12 ? 'AM' : 'PM';
                    const h12 = ((hh % 12) || 12);
                    opt.textContent = `${h12}:${mm.toString().padStart(2,'0')} ${ampm}`;
                    timeSelect.appendChild(opt);
                });

                timeSelect.disabled = false;
            })
            .catch(() => {
                if (loadingMsg) loadingMsg.style.display = 'none';
                timeSelect.innerHTML = '<option value="">Error loading slots</option>';
                timeSelect.disabled = true;
            });
    }

    dateInput.addEventListener('change', loadSlots);

    document.querySelectorAll('input[name="patient_type"]').forEach(r => {
        r.addEventListener('change', loadSlots);
    });
}());

// ── Dashboard: notes AJAX ───────────────────────────────────
(function () {
    const notesForm = document.getElementById('notes-form');
    if (!notesForm) return;

    notesForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const url  = notesForm.dataset.url;
        const data = new FormData(notesForm);

        fetch(url, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            body: data,
        })
        .then(r => r.json())
        .then(res => {
            const msg = document.getElementById('notes-msg');
            if (msg) {
                msg.textContent = res.success ? 'Saved successfully.' : 'Error saving. Please try again.';
                msg.className = res.success ? 'field-success' : 'field-error';
                msg.style.display = 'block';
                setTimeout(() => { msg.style.display = 'none'; }, 3000);
            }
        });
    });
}());

// ── Dashboard: status AJAX ──────────────────────────────────
(function () {
    const statusForm = document.getElementById('status-form');
    if (!statusForm) return;

    statusForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const url  = statusForm.dataset.url;
        const data = new FormData(statusForm);

        fetch(url, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            body: data,
        })
        .then(r => r.json())
        .then(res => {
            if (res.success) {
                const badge = document.getElementById('status-badge');
                if (badge) {
                    badge.textContent = res.status_display;
                    badge.className = `badge badge-${res.status}`;
                }
                const msg = document.getElementById('status-msg');
                if (msg) {
                    msg.textContent = 'Status updated.';
                    msg.style.display = 'block';
                    setTimeout(() => { msg.style.display = 'none'; }, 3000);
                }
            }
        });
    });
}());

// ── Mobile navbar toggle ─────────────────────────────────────
(function () {
    const btn   = document.querySelector('.navbar-menu-btn');
    const links = document.querySelector('.navbar-links');
    if (!btn || !links) return;
    btn.addEventListener('click', () => links.classList.toggle('open'));
}());

// ── Radio option visual styling ──────────────────────────────
document.querySelectorAll('.radio-option input[type="radio"]').forEach(radio => {
    radio.addEventListener('change', function () {
        const name = this.name;
        document.querySelectorAll(`.radio-option input[name="${name}"]`).forEach(r => {
            r.closest('.radio-option').classList.toggle('selected', r.checked);
        });
    });
    // Init on page load
    if (radio.checked) radio.closest('.radio-option').classList.add('selected');
});

// ── Multi-card Carousel (Specialisations) ───────────────────
(function () {
    document.querySelectorAll('.mc-carousel-wrapper').forEach(function (wrapper) {
        const id     = wrapper.dataset.carousel;
        const track  = document.getElementById(id + 'Track');
        const dots   = document.getElementById(id + 'Dots');
        const prev   = wrapper.querySelector('.mc-btn-prev');
        const next   = wrapper.querySelector('.mc-btn-next');
        if (!track) return;

        const slides = track.querySelectorAll('.mc-slide');
        const total  = slides.length;
        let   current = 0;

        function visibleCount() {
            const w = wrapper.offsetWidth;
            if (w >= 700) return 3;
            if (w >= 460) return 2;
            return 1;
        }

        function slideWidth() {
            return slides[0] ? slides[0].offsetWidth + 16 : 0; /* 16 = 1rem gap */
        }

        function maxIndex() {
            return Math.max(0, total - visibleCount());
        }

        function buildDots() {
            if (!dots) return;
            dots.innerHTML = '';
            const pages = maxIndex() + 1;
            for (let i = 0; i < pages; i++) {
                const d = document.createElement('button');
                d.className = 'carousel-dot' + (i === 0 ? ' active' : '');
                d.setAttribute('aria-label', 'Page ' + (i + 1));
                d.addEventListener('click', function () { goTo(i); });
                dots.appendChild(d);
            }
        }

        function updateDots() {
            if (!dots) return;
            dots.querySelectorAll('.carousel-dot').forEach(function (d, i) {
                d.classList.toggle('active', i === current);
            });
        }

        function updateArrows() {
            if (prev) prev.disabled = current === 0;
            if (next) next.disabled = current >= maxIndex();
        }

        function goTo(index) {
            current = Math.min(Math.max(index, 0), maxIndex());
            track.style.transform = 'translateX(-' + (current * slideWidth()) + 'px)';
            updateDots();
            updateArrows();
        }

        if (prev) prev.addEventListener('click', function () { goTo(current - 1); });
        if (next) next.addEventListener('click', function () { goTo(current + 1); });

        // Touch swipe
        let tx = 0;
        track.addEventListener('touchstart', function (e) { tx = e.touches[0].clientX; }, { passive: true });
        track.addEventListener('touchend', function (e) {
            const diff = tx - e.changedTouches[0].clientX;
            if (Math.abs(diff) > 40) { diff > 0 ? goTo(current + 1) : goTo(current - 1); }
        }, { passive: true });

        // Re-init on resize (visible count may change)
        window.addEventListener('resize', function () { buildDots(); goTo(Math.min(current, maxIndex())); });

        buildDots();
        updateArrows();
    });
}());

// ── Testimonials Carousel ────────────────────────────────────
(function () {
    const track    = document.getElementById('testimonialTrack');
    const prevBtn  = document.getElementById('testimonialPrev');
    const nextBtn  = document.getElementById('testimonialNext');
    const dotsWrap = document.getElementById('testimonialDots');
    if (!track) return;

    const slides = track.querySelectorAll('.testimonial-slide');
    const total  = slides.length;
    let   current = 0;
    let   timer;

    // Build dots
    slides.forEach((_, i) => {
        const dot = document.createElement('button');
        dot.className = 'carousel-dot' + (i === 0 ? ' active' : '');
        dot.setAttribute('aria-label', `Slide ${i + 1}`);
        dot.addEventListener('click', () => goTo(i));
        dotsWrap.appendChild(dot);
    });

    function goTo(index) {
        current = (index + total) % total;
        track.style.transform = `translateX(-${current * 100}%)`;
        dotsWrap.querySelectorAll('.carousel-dot').forEach((d, i) => {
            d.classList.toggle('active', i === current);
        });
    }

    function next() { goTo(current + 1); }
    function prev() { goTo(current - 1); }

    function startAuto() {
        timer = setInterval(next, 5000);
    }

    function stopAuto() {
        clearInterval(timer);
    }

    prevBtn.addEventListener('click', () => { stopAuto(); prev(); startAuto(); });
    nextBtn.addEventListener('click', () => { stopAuto(); next(); startAuto(); });

    // Pause on hover
    track.closest('.carousel-wrapper').addEventListener('mouseenter', stopAuto);
    track.closest('.carousel-wrapper').addEventListener('mouseleave', startAuto);

    // Touch/swipe support
    let touchStartX = 0;
    track.addEventListener('touchstart', e => { touchStartX = e.touches[0].clientX; }, { passive: true });
    track.addEventListener('touchend', e => {
        const diff = touchStartX - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 40) {
            stopAuto();
            diff > 0 ? next() : prev();
            startAuto();
        }
    }, { passive: true });

    startAuto();

    // ── Read-more toggle ──────────────────────────────────────
    track.querySelectorAll('.testimonial-card').forEach(function (card) {
        const text = card.querySelector('.testimonial-text');
        const btn  = card.querySelector('.testimonial-read-more');
        if (!text || !btn) return;

        // Apply clamp and check whether text actually overflows
        text.classList.add('clamped');
        if (text.scrollHeight > text.clientHeight + 2) {
            btn.style.display = 'block';
        }

        btn.addEventListener('click', function () {
            const nowClamped = text.classList.toggle('clamped');
            btn.textContent = nowClamped ? 'Read more' : 'Read less';
        });
    });
}());

// ── Scroll Reveal (IntersectionObserver) ─────────────────────
(function () {
    if (!window.IntersectionObserver) return;

    const selector = [
        '.section-title', '.section-subtitle',
        '.card', '.spec-card', '.step',
        '.womens-card', '.opd-card', '.stat-card',
        '.appt-card', '.form-card', '.testimonials-section .section-title',
        '.testimonials-section .section-subtitle'
    ].join(', ');

    const els = document.querySelectorAll(selector);
    if (!els.length) return;

    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                // stagger siblings inside the same parent grid/row
                const siblings = Array.from(entry.target.parentElement.querySelectorAll('.reveal'));
                const idx = siblings.indexOf(entry.target);
                entry.target.style.transitionDelay = (idx * 80) + 'ms';
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.10 });

    els.forEach(function (el) {
        el.classList.add('reveal');
        observer.observe(el);
    });
}());
