import { useState, useEffect } from 'react';

const useDeals = (viewMode, selectedMerchant) => {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState('');
  const [isScraping, setIsScraping] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalProducts, setTotalProducts] = useState(0);
  const [pageSize, setPageSize] = useState(50);

  const fetchDeals = async (page = 1, merchant = selectedMerchant) => {
    setLoading(true);
    setError(null);
    const current_page_size = viewMode === 'grid' ? 50 : 20;
    setPageSize(current_page_size);

    let url = `/api/deals?page=${page}&page_size=${current_page_size}`;
    if (merchant && merchant !== 'All') {
      url += `&merchant=${merchant}`;
    }

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Failed to fetch deals');
      }
      const data = await response.json();

      const statusResponse = await fetch('/api/scraper_status');
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setIsScraping(statusData.is_scraping);
      }

      const products = data.products || [];
      setDeals(products);
      setTotalProducts(data.total_products);
      setCurrentPage(data.page);
      if (data.last_updated) {
        setLastUpdated(data.last_updated);
      }
    } catch (err) {
      setError('Failed to fetch deals. Is the backend server running ?');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDeals(1, selectedMerchant);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [viewMode, selectedMerchant]);

  return {
    deals,
    loading,
    error,
    lastUpdated,
    isScraping,
    currentPage,
    totalProducts,
    pageSize,
    fetchDeals,
  };
};

export default useDeals;
