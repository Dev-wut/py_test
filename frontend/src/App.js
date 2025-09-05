import React, { useState } from 'react';
import 'antd/dist/reset.css';
import { Routes, Route } from 'react-router-dom';
import html2canvas from 'html2canvas';
import ScraperCriteria from './ScraperCriteria';
import {
  Layout,
  Row,
  Col,
  Spin,
  Alert,
  Typography,
  Button,
  Empty,
  Space,
  Tag,
  message
} from 'antd';
import AppHeader from './components/AppHeader';
import GridCard from './components/GridCard';
import FacebookCard from './components/FacebookCard';
import PaginationControls from './components/PaginationControls';
import useDeals from './hooks/useDeals';
import useMerchants from './hooks/useMerchants';

const { Content, Footer } = Layout;
const { Text } = Typography;

const App = () => {
  const [messageApi, contextHolder] = message.useMessage();
  const [viewMode, setViewMode] = useState('grid');
  const [selectedMerchant, setSelectedMerchant] = useState('All');

  const {
    deals,
    loading,
    error,
    lastUpdated,
    isScraping,
    currentPage,
    totalProducts,
    pageSize,
    fetchDeals,
  } = useDeals(viewMode, selectedMerchant);

  const { merchants } = useMerchants();

  const handlePageChange = (page) => {
    fetchDeals(page, selectedMerchant);
  };

  const handleMerchantSelect = (merchant) => {
    setSelectedMerchant(merchant);
  };

  const calculateSavings = (originalPrice, currentPrice) => {
    const original = parseFloat(String(originalPrice).replace(/,/g, ''));
    const current = parseFloat(String(currentPrice).replace(/,/g, ''));
    if (isNaN(original) || isNaN(current)) return 0;
    const savings = original - current;
    return new Intl.NumberFormat('th-TH').format(savings);
  };

  const handleDownload = async (cardRef) => {
    if (cardRef.current) {
      const downloadButton = cardRef.current.parentElement.querySelector('.download-button');
      if (downloadButton) {
        downloadButton.style.display = 'none';
      }

      const canvas = await html2canvas(cardRef.current, {
        backgroundColor: null,
        useCORS: true,
        allowTaint: false,
        scale: 2,
      });

      if (downloadButton) {
        downloadButton.style.display = 'block';
      }

      canvas.toBlob((blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'product-card.png';
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
      }, 'image/png', 1.0);
    }
  };

  const renderContent = () => {
    if (loading) {
      return (
        <div className="loading-spinner-container" style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" tip="Loading Deals..." />
        </div>
      );
    }

    if (error) {
      return <Alert message="Error" description={error} type="error" showIcon />;
    }

    if (deals.length === 0) {
      return <Empty description={`No deals found for ${selectedMerchant}.`} />;
    }

    if (viewMode === 'facebook') {
      return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '32px' }}>
          {deals.map((deal, index) => (
            <FacebookCard
              product={deal}
              key={index}
              onDownload={handleDownload}
              calculateSavings={calculateSavings}
            />
          ))}
        </div>
      );
    }

    return (
      <Row gutter={[24, 24]} align="stretch">
        {deals.map((deal, index) => (
          <Col xs={24} sm={12} md={8} lg={6} key={`${deal.product_url}-${index}`}>
            <GridCard
              product={deal}
              onDownload={handleDownload}
              calculateSavings={calculateSavings}
            />
          </Col>
        ))}
      </Row>
    );
  };

  return (
    <Routes>
      <Route
        path="/"
        element={
          <Layout style={{ minHeight: '100vh' }}>
            {contextHolder}
            <AppHeader
              totalProducts={totalProducts}
              loading={loading}
              onRefresh={() => fetchDeals(1, selectedMerchant)}
            />
            <Content style={{ padding: '24px' }}>
              {lastUpdated && (
                <Text type="secondary" style={{ textAlign: 'center', display: 'block', marginBottom: '1rem' }}>
                  Last Updated: {lastUpdated}
                </Text>
              )}
              {isScraping && (
                <Alert message="Scraping in progress..." type="info" showIcon style={{ marginBottom: '1rem' }} />
              )}
              <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '24px' }}>
                <Space>
                  <Button
                    type={viewMode === 'facebook' ? 'primary' : 'default'}
                    onClick={() => setViewMode('facebook')}
                  >
                    Facebook Cards (1200x630)
                  </Button>
                  <Button
                    type={viewMode === 'grid' ? 'primary' : 'default'}
                    onClick={() => setViewMode('grid')}
                  >
                    การ์ดแบบปกติ
                  </Button>
                </Space>
              </div>
              <div
                style={{
                  background: '#fff',
                  padding: '16px',
                  borderRadius: '8px',
                  marginBottom: '24px',
                  textAlign: 'center',
                }}
              >
                <Text strong>Filter by Merchant:</Text>
                <Space size={[0, 8]} wrap>
                  {merchants.map((merchant) => (
                    <Tag.CheckableTag
                      key={merchant}
                      checked={selectedMerchant === merchant}
                      onChange={() => handleMerchantSelect(merchant)}
                      style={{ fontSize: '14px', padding: '6px 12px', margin: '4px' }}
                    >
                      {merchant}
                    </Tag.CheckableTag>
                  ))}
                </Space>
              </div>
              <div className="card-list-container" style={{ padding: 24, minHeight: 308, borderRadius: '8px' }}>
                {renderContent()}
              </div>
              <PaginationControls
                currentPage={currentPage}
                totalProducts={totalProducts}
                pageSize={pageSize}
                onPageChange={handlePageChange}
              />
            </Content>
            <Footer style={{ textAlign: 'center' }}>
              PriceZA Scraper ©2025 Created with Gemini
            </Footer>
          </Layout>
        }
      />
      <Route path="/scraper-criteria" element={<ScraperCriteria />} />
    </Routes>
  );
};

export default App;
