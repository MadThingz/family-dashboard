/**
 * app.js
 *
 * Responsibility: fetch data/*.json and render it into the page.
 */

// -------------------------------------------------------------------------
// Utilities
// -------------------------------------------------------------------------

async function fetchData(filename) {
  try {
    const response = await fetch(`data/${filename}`, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`${filename} responded with ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`[app] Failed to load ${filename}:`, error);
    return null;
  }
}

const WEATHER_ICONS = {
  clear: "☀️",
  "mostly-clear": "🌤️",
  "partly-cloudy": "⛅",
  cloudy: "☁️",
  fog: "🌫️",
  drizzle: "🌦️",
  rain: "🌧️",
  snow: "❄️",
  thunderstorm: "⛈️",
};

function formatFullDate(date) {
  return date.toLocaleDateString("en-GB", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });
}

function formatTime(date) {
  return date.toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

// -------------------------------------------------------------------------
// Feature: Page header (date)
// -------------------------------------------------------------------------

function renderHeaderDate() {
  const el = document.getElementById("header-date");
  if (!el) return;
  el.textContent = formatFullDate(new Date());
}

// -------------------------------------------------------------------------
// Feature: Overview card (Weather + Clock)
// -------------------------------------------------------------------------

function renderWeather(weather) {
  const container = document.getElementById("weather-content");
  if (!container) return;

  if (!weather) {
    container.innerHTML = `<p class="card__empty">Weather unavailable</p>`;
    return;
  }

  const icon = WEATHER_ICONS[weather.icon] ?? "🌡️";

  container.innerHTML = `
    <div class="overview-card__weather">
      <span class="overview-card__temp">${icon} ${weather.temperature_c}°</span>
      <span class="overview-card__condition">${weather.condition}</span>
      <span class="overview-card__range">H:${weather.high_c}° L:${weather.low_c}°</span>
    </div>
  `;
}

function renderClock() {
  const container = document.getElementById("clock-content");
  if (!container) return;

  function tick() {
    const now = new Date();
    container.innerHTML = `
      <div class="overview-card__clock">
        <span class="overview-card__time">${formatTime(now)}</span>
        <span class="overview-card__location">${document.body.dataset.locationLabel ?? ""}</span>
      </div>
    `;
  }

  tick();
  setInterval(tick, 1000 * 30);
}

async function loadOverview() {
  const weather = await fetchData("weather.json");
  if (weather) {
    document.body.dataset.locationLabel = weather.location;
  }
  renderWeather(weather);
  renderClock();
}

// -------------------------------------------------------------------------
// Feature: Shopping List
// -------------------------------------------------------------------------

async function loadShopping() {
  const shopping = await fetchData("shopping.json");
  renderShopping(shopping);
}

function renderShopping(shopping) {
  const container = document.getElementById("shopping-list");
  if (!container) return;

  if (!shopping || !shopping.items || shopping.items.length === 0) {
    container.innerHTML = `<p class="card__empty">No items yet</p>`;
    return;
  }

  const itemsHtml = shopping.items
    .map(
      (item) => `
    <li class="shopping-item">
      <input
        type="checkbox"
        class="shopping-item__checkbox"
        ${item.checked ? "checked" : ""}
        disabled
      />
      <span class="shopping-item__text ${item.checked ? "shopping-item__text--done" : ""}">
        ${item.name}
      </span>
    </li>
  `
    )
    .join("");

  container.innerHTML = `<ul class="shopping-list">${itemsHtml}</ul>`;
}

// -------------------------------------------------------------------------
// Init
// -------------------------------------------------------------------------

function init() {
  renderHeaderDate();
  loadOverview();
  loadShopping();
}

document.addEventListener("DOMContentLoaded", init);
