'use strict';
 
const request = require('supertest');
const app = require('./index.js');
 
describe('${{ values.serviceName }}', () => {
  test('GET /health responde 200 y status UP', async () => {
    const res = await request(app).get('/health');
    expect(res.statusCode).toBe(200);
    expect(res.body.status).toBe('UP');
  });
 
  test('GET / responde 200', async () => {
    const res = await request(app).get('/');
    expect(res.statusCode).toBe(200);
  });
 
  test('una ruta inexistente responde 404', async () => {
    const res = await request(app).get('/no-existe');
    expect(res.statusCode).toBe(404);
  });
});