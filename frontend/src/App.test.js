import { render, screen } from '@testing-library/react';
import AppHeader from './components/AppHeader';

test('renders header title', () => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation(() => ({
      matches: false,
      media: '',
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    })),
  });
  render(<AppHeader totalProducts={0} loading={false} onRefresh={() => {}} />);
  const headerElement = screen.getByText(/PriceZA Deals Za/i);
  expect(headerElement).toBeInTheDocument();
});
