import { useState, useEffect } from 'react';

const useOwnerDeals = () => {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalProducts, setTotalProducts] = useState(0);
  const [pageSize, setPageSize] = useState(50);

  const fetchDeals = async (page = 1) => {
    setLoading(true);
    setError(null);

    let url = `/api/owner_deals?page=${page}&page_size=${pageSize}`;

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Failed to fetch owner deals');
      }
      const data = await response.json();
      console.log('Owner Deals API response', data);

      const products = data.products || [];
      setDeals(products);
      setTotalProducts(data.total_products);
      setCurrentPage(data.page);
    } catch (err) {
      setError('Failed to fetch owner deals. Is the backend server running ?');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDeals(1);
  }, []);

  return {
    deals,
    loading,
    error,
    currentPage,
    totalProducts,
    pageSize,
    fetchDeals,
  };
};

export default useOwnerDeals;
