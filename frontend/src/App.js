import React, { useState, useEffect } from 'react';
import axios from 'axios';
import 'antd/dist/reset.css';
import { Routes, Route } from 'react-router-dom';
import ScraperCriteria from './ScraperCriteria';
import {
  Layout,
  Row,
  Col,
  Card,
  Spin,
  Alert,
  Typography,
  Statistic,
  Button,
  Empty,
  Space,
  Tag,
  message
} from 'antd';
import { SyncOutlined, ShoppingCartOutlined, CopyOutlined } from '@ant-design/icons';

const { Header, Content, Footer } = Layout;
const { Title, Text, Paragraph } = Typography;

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
const API_URL = `${API_BASE_URL}/api/deals`;

// Custom Logo Component
const AppLogo = () => (
    <div className="logo-container" style={{ display: 'flex', alignItems: 'center', color: 'white' }}>
        <ShoppingCartOutlined style={{ fontSize: '32px' }} />
        <Title level={3} style={{ color: 'white', margin: '0 0 0 12px', whiteSpace: 'nowrap' }}>
            PriceZA Deals
        </Title>
    </div>
);

const App = () => {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState('');
  const [merchants, setMerchants] = useState([]);
  const [selectedMerchant, setSelectedMerchant] = useState('All');
  const [isScraping, setIsScraping] = useState(false);
  const [messageApi, contextHolder] = message.useMessage();

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(API_URL);
      const statusResponse = await axios.get(`${API_BASE_URL}/api/scraper_status`);
      setIsScraping(statusResponse.data.is_scraping);
      const products = response.data.products || [];
      setDeals(products);

      if (response.data.timestamp) {
        const formattedDate = new Date(response.data.timestamp).toLocaleString();
        setLastUpdated(formattedDate);
      }

      if (products.length > 0) {
        const allMerchants = ['All', ...new Set(products.map(deal => deal.merchant))];
        setMerchants(allMerchants);
      }

    } catch (err) {
      setError('Failed to fetch deals. Is the backend server running ?');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleMerchantSelect = (merchant) => {
    setSelectedMerchant(merchant);
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

    const filteredDeals = selectedMerchant === 'All'
      ? deals
      : deals.filter(deal => deal.merchant === selectedMerchant);

    if (filteredDeals.length === 0) {
        return <Empty description={`No deals found for ${selectedMerchant}.`} />
    }

    return (
      // By setting align="stretch", all columns in a row are forced to be the same height.
      <Row gutter={[24, 24]} align="stretch">
        {filteredDeals.map((deal, index) => (
          <Col xs={24} sm={24} md={12} lg={12} xl={12} key={`${deal.product_url}-${index}`}>
            <div className="custom-ribbon-wrapper">
              <div className="custom-ribbon">{deal.discount}</div>
              <a href={deal.product_url} target="_blank" rel="noopener noreferrer" className="card-link" style={{ textDecoration: 'none', width: '100%', height: '100%', borderRadius: '8px' }}>
                <Card
                    style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
                    bodyStyle={{ flexGrow: 1, display: 'flex', flexDirection: 'column', padding: '16px'}}
                    cover={<img alt={deal.title} src={deal.image_url} style={{ height: 180, objectFit: 'contain', padding: '16px' }} />}
                >
                    <div className="merchant-image-container" style={{ textAlign: 'center', background: '#fafafa', padding: '8px 0', borderTop: '1px solid #f0f0f0', borderBottom: '1px solid #f0f0f0', marginBottom: '1rem' }}>
                        <img src={deal.merchant_image} alt={deal.merchant} style={{height: '24px', maxWidth: '80px', objectFit: 'contain'}}/>
                    </div>
                    {/* This inner div is the key to making content fill the card height */}
                    <div className="card-content-container" style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                        <Paragraph style={{ marginBottom: '1rem' }} strong>{deal.title}</Paragraph>
                        <Button 
                            type="dashed" 
                            size="small" 
                            icon={<CopyOutlined />} 
                            onClick={(e) => {
                                e.preventDefault(); // Prevent navigating to product URL
                                navigator.clipboard.writeText(deal.title)
                                    .then(() => messageApi.success('Title copied!'))
                                    .catch(() => messageApi.error('Failed to copy title.'));
                            }}
                            style={{ marginBottom: '1rem' }}
                        >
                            Copy Title
                        </Button>
                        <div className="price-container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                            <div>
                                <Text delete type="secondary">฿{deal.original_price}</Text>
                                <Title level={4} style={{ color: '#cf1322', margin: 0 }}>฿{deal.price}</Title>
                            </div>
                        </div>
                    </div>
                </Card>
              </a>
            </div>
          </Col>
        ))}
      </Row>
    );
  };

  return (
    <Routes>
      <Route path="/" element={
        <Layout style={{ minHeight: '100vh' }}>
          {contextHolder}
          <Header className="app-header" style={{ background: '#001529' }}>
            <div className="header-container" style={{height: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                <AppLogo />
                <div className="statistic-container-mobile-hide" style={{ flexGrow: 1, textAlign: 'center' }}>
                    <Statistic
                        title={<Text style={{color: '#a6adb4'}}>Deals Found</Text>}
                        value={deals.length}
                        valueStyle={{color: '#fff'}}
                    />
                </div>
                <Space align="center" size="small" wrap>
                    <Row className="header-buttons-row" gutter={[8, 8]} style={{ flexGrow: 1, justifyContent: 'flex-end' }}>
                        <Col xs={24} sm={12} md={12} lg={12} xl={12}>
                            <Button type="default" ghost onClick={() => window.open('/scraper-criteria', '_blank')} style={{ width: '100%' }}>
                                Scraper Config
                            </Button>
                        </Col>
                        <Col xs={24} sm={12} md={12} lg={12} xl={12}>
                            <Button type="primary" ghost icon={<SyncOutlined />} onClick={fetchData} loading={loading} style={{ width: '100%' }}>
                                Refresh
                            </Button>
                        </Col>
                    </Row>
                </Space>
            </div>
          </Header>
          <Content style={{ padding: '24px' }}>
            {lastUpdated && <Text type="secondary" style={{ textAlign:'center', display: 'block', marginBottom: '1rem' }}>Last Updated: {lastUpdated}</Text>}
            {isScraping && <Alert message="Scraping in progress..." type="info" showIcon style={{ marginBottom: '1rem' }} />}
            <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', marginBottom: '24px', textAlign: 'center' }}>
                <Text strong>Filter by Merchant:</Text>
                <Space size={[0, 8]} wrap>
                    {merchants.map(merchant => (
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
          </Content>
          <Footer style={{ textAlign: 'center' }}>
            PriceZA Scraper ©2025 Created with Gemini
          </Footer>
        </Layout>
      } />
      <Route path="/scraper-criteria" element={<ScraperCriteria />} />
    </Routes>
  );
};

export default App;