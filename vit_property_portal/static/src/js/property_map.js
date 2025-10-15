/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.VitPropertyMap = publicWidget.Widget.extend({
    selector: ".property-map",

    start() {
        this._initMap();
        return this._super(...arguments);
    },

    _initMap() {
        const mapContainer = this.el;
        if (!mapContainer) return;

        const lat = parseFloat(mapContainer.dataset.lat);
        const lon = parseFloat(mapContainer.dataset.lon);
        if (!lat || !lon) {
            console.warn("VitPropertyMap: Latitude/Longitude not available.");
            return;
        }

        this._ensureLeafletAssets().then(() => {
            this._renderMap(mapContainer, lat, lon);
        });
    },

    _ensureLeafletAssets() {
        return new Promise((resolve) => {
            if (window.L) return resolve();

            const leafletCss = document.createElement("link");
            leafletCss.rel = "stylesheet";
            leafletCss.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
            document.head.appendChild(leafletCss);

            const leafletJs = document.createElement("script");
            leafletJs.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
            leafletJs.onload = () => resolve();
            document.body.appendChild(leafletJs);
        });
    },

    _renderMap(container, lat, lon) {
        const map = L.map(container).setView([lat, lon], 15);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution: "&copy; OpenStreetMap contributors",
        }).addTo(map);

        L.marker([lat, lon])
            .addTo(map)
            .bindPopup(`<b>${container.dataset.name}</b><br>${container.dataset.address}`)
            .openPopup();

        const tab = document.querySelector('a[data-bs-target="#rincian"]');
        if (tab) {
            tab.addEventListener("shown.bs.tab", () => {
                map.invalidateSize();
            });
        }
    },
});

document.addEventListener("DOMContentLoaded", () => {
    const maps = document.querySelectorAll(".property-map");
    maps.forEach((el) => {
        publicWidget.attachTo(el);
    });
});
