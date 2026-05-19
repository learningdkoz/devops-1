// k6-скрипт нагрузочного теста (CDL-12). Стартует параллельные VU,
// валидирует p95-латенси и error-rate. Запуск: `k6 run scripts/perf.js`.
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },   // плавный разгон
    { duration: '1m',  target: 50 },   // номинал
    { duration: '30s', target: 0  },   // ramp-down
  ],
  thresholds: {
    http_req_failed:   ['rate<0.01'],         // меньше 1% ошибок
    http_req_duration: ['p(95)<200'],         // p95 < 200ms
  },
};

const BASE = __ENV.BASE_URL || 'http://localhost:8080';

export default function () {
  const r = http.get(`${BASE}/hi?name=World`);
  check(r, {
    'status 200': (res) => res.status === 200,
    'has Hi':     (res) => res.body && res.body.indexOf('Hi') !== -1,
  });
  sleep(0.1);
}
