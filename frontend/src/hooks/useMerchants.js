import { useState, useEffect } from 'react';

const useMerchants = () => {
  const [merchants, setMerchants] = useState([]);

  const fetchMerchants = async () => {
    try {
      const response = await fetch('/api/merchants');
      if (!response.ok) {
        throw new Error('Failed to fetch merchants');
      }
      const data = await response.json();
      setMerchants(['All', ...data]);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchMerchants();
  }, []);

  return { merchants, fetchMerchants };
};

export default useMerchants;
