export default {
  test: {
    environment: 'jsdom',
    include: ['tests/spa/**/*.test.mjs'],
    globals: true
  }
};
