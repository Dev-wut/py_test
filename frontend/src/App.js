import React, { useState, useEffect, useRef } from 'react';
import 'antd/dist/reset.css';
import { Routes, Route } from 'react-router-dom';
import { LazyLoadImage } from 'react-lazy-load-image-component';
import 'react-lazy-load-image-component/src/effects/blur.css';
import html2canvas from 'html2canvas';
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
import { SyncOutlined, ShoppingCartOutlined, CopyOutlined, FacebookOutlined, DownloadOutlined } from '@ant-design/icons';

const { Header, Content, Footer } = Layout;
const { Title, Text, Paragraph } = Typography;


// Custom Logo Component
const AppLogo = () => (
    <div className="logo-container" style={{ display: 'flex', alignItems: 'center', color: 'white' }}>
        <ShoppingCartOutlined style={{ fontSize: '32px' }} />
        <Title level={3} style={{ color: 'white', margin: '0 0 0 12px', whiteSpace: 'nowrap' }}>
            PriceZA Deals Za
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
  const [viewMode, setViewMode] = useState('grid');

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/deals');
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
      const filteredProducts = products.filter(p => p.merchant !== 'UNNAMED');
      setDeals(filteredProducts);

      if (data.timestamp) {
        const formattedDate = new Date(data.timestamp).toLocaleString();
        setLastUpdated(formattedDate);
      }

      if (filteredProducts.length > 0) {
        const allMerchants = ['All', ...new Set(filteredProducts.map(deal => deal.merchant))];
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

  const getStoreColor = (store) => {
    const colors = {
      'LAZADA': '#FF6600',
      'SHOPEE': '#EE4D2D',
      'TIKTOK': '#000000',
      'TIKTOK-SEA': '#333333',
      'B2S': '#1E90FF',
      'CENTRAL_NEW': '#8A2BE2',
      'SAMSUNG-AFFILIATE': '#00008B',
      'ISTUDIO_N': '#555555',
      'HOMEPRO': '#008000',
      '2BESHOP': '#9932CC',
      'REV': '#FF0000',
      'OFM': '#4B0082',
      'UNNAMED': '#808080',
      'BANANA': '#FFD700',
      'STUDIO7': '#FF69B4',
      'NOCNOC': '#00CED1',
      'ICC': '#3CB371',
      'DOTLIFE': '#1E90FF',
      'ALLONLINE_AFFILIATE': '#9370DB',
      'CASECLUB1': '#FF4500',
      '1577SHOP': '#FFA500',
      'SINGHANEW': '#32CD32',
      'MAKROPRO': '#20B2AA',
      'PROSPACE': '#708090'
    };
    return colors[store] || '#808080';
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

  const FacebookCard = ({ product }) => {
    const cardRef = useRef(null);
    return (
      <div style={{ position: 'relative' }}>
        <Button 
          className="download-button"
          icon={<DownloadOutlined />} 
          onClick={() => handleDownload(cardRef)}
          style={{ position: 'absolute', top: '24px', right: '-50px', zIndex: 2 }}
        />
        <div ref={cardRef} style={{ width: '1200px', height: '630px', background: 'white', borderRadius: '24px', boxShadow: '0 10px 30px rgba(0,0,0,0.1)', overflow: 'hidden', border: '1px solid #e8e8e8' }}>
          <Row style={{ height: '100%' }}>
            <Col span={12} style={{ position: 'relative', background: '#fafafa' }}>
              <Tag color={getStoreColor(product.merchant)} style={{ position: 'absolute', top: '24px', left: '24px', padding: '8px 16px', borderRadius: '16px', fontSize: '16px', fontWeight: 'bold', zIndex: 1 }}>
                {product.merchant}
              </Tag>
              <Tag color="#f5222d" style={{ position: 'absolute', top: '24px', right: '24px', padding: '8px 16px', borderRadius: '16px', fontSize: '16px', fontWeight: 'bold', zIndex: 1 }}>
                {product.discount}
              </Tag>
              <LazyLoadImage
                alt={product.title}
                effect="blur"
                src={`/api/proxy-image?url=${encodeURIComponent(product.image_url)}`}
                width="100%"
                height="100%"
                style={{ objectFit: 'cover' }}
                onError={(e) => { e.target.src = "https://via.placeholder.com/600x630/e5e7eb/6b7280?text=No+Image"; }}
              />
            </Col>
            <Col span={12} style={{ padding: '32px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <Title level={2} style={{ marginBottom: '24px', lineHeight: 1.3, maxHeight: '150px', overflow: 'hidden' }}>{product.title}</Title>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <Title level={1} style={{ margin: 0, color: '#f5222d' }}>฿{product.price}</Title>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <Text delete style={{ fontSize: '24px' }}>฿{product.original_price}</Text>
                  <Tag color="#fff1f0" style={{ color: '#f5222d', padding: '8px 12px', borderRadius: '8px', fontSize: '18px', fontWeight: 'bold' }}>
                    ประหยัด ฿{calculateSavings(product.original_price, product.price)}
                  </Tag>
                </div>
              </div>
              <div style={{ background: 'linear-gradient(to right, #1890ff, #9013FE)', color: 'white', padding: '24px', margin: '-32px', marginTop: '32px', textAlign: 'center' }}>
                <Space size="large">
                  <FacebookOutlined style={{ fontSize: '24px' }} />
                  <Text style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>โปรดีบอกต่อ Prod</Text>
                  <ShoppingCartOutlined style={{ fontSize: '24px' }} />
                </Space>
              </div>
            </Col>
          </Row>
        </div>
      </div>
    )
  };

  const GridCard = ({ product }) => {
    const cardRef = useRef(null);
    return (
      <div style={{ position: 'relative', height: '100%' }}>
        <Button 
          className="download-button"
          icon={<DownloadOutlined />} 
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleDownload(cardRef); }}
          style={{ position: 'absolute', top: '12px', right: '-40px', zIndex: 2 }}
        />
        <div ref={cardRef} style={{ height: '100%' }}>
          <a href={product.product_url} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none', height: '100%', display: 'block' }}>
            <Card
              hoverable
              style={{ borderRadius: '16px', overflow: 'hidden', border: '2px solid #f0f0f0', height: '100%' }}
              cover={
                <div style={{ position: 'relative', height: '180px', background: '#f5f5f5' }}>
                  <Tag 
                    color={getStoreColor(product.merchant)} 
                    style={{ position: 'absolute', top: '12px', left: '12px', borderRadius: '9999px', fontSize: '10px', fontWeight: 'bold', zIndex: 1 }}
                  >
                    {product.merchant}
                  </Tag>
                  <Tag 
                    color="#f5222d" 
                    style={{ position: 'absolute', top: '12px', right: '12px', borderRadius: '9999px', fontSize: '10px', fontWeight: 'bold', zIndex: 1 }}
                  >
                    {product.discount}
                  </Tag>
                  <LazyLoadImage
                    alt={product.title}
                    effect="blur"
                    src={`/api/proxy-image?url=${encodeURIComponent(product.image_url)}`}
                    width="100%"
                    height="100%"
                    style={{ objectFit: 'cover' }}
                    onError={(e) => { e.target.src = "https://via.placeholder.com/300x300/e5e7eb/6b7280?text=No+Image"; }}
                  />
                </div>
              }
              bodyStyle={{ padding: '16px', display: 'flex', flexDirection: 'column', flexGrow: 1 }}
            >
              <div style={{ flexGrow: 1 }}>
                <Paragraph strong style={{ fontSize: '12px', lineHeight: '1.4', height: '50px', overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical' }}>
                  {product.title}
                </Paragraph>
                
                <div style={{ margin: '12px 0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Title level={5} style={{ margin: 0, color: '#f5222d' }}>฿{product.price}</Title>
                    <Tag color="#fff1f0" style={{ color: '#f5222d', fontSize: '10px', fontWeight: 'semibold', borderRadius: '4px' }}>
                      ประหยัด ฿{calculateSavings(product.original_price, product.price)}
                    </Tag>
                  </div>
                  <Text delete type="secondary" style={{ fontSize: '12px' }}>฿{product.original_price}</Text>
                </div>
              </div>

              <div style={{ background: 'linear-gradient(to right, #4A90E2, #9013FE)', color: 'white', padding: '8px', textAlign: 'center', borderRadius: '8px', marginTop: 'auto' }}>
                <Text style={{ color: 'white', fontSize: '12px', fontWeight: 'medium' }}>
                  โปรดีบอกต่อ Prod
                </Text>
              </div>
            </Card>
          </a>
        </div>
      </div>
    )
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

    if (viewMode === 'facebook') {
      return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '32px' }}>
          {filteredDeals.map((deal, index) => (
            <FacebookCard product={deal} key={index} />
          ))}
        </div>
      );
    }

    return (
      <Row gutter={[24, 24]} align="stretch">
        {filteredDeals.map((deal, index) => (
          <Col xs={24} sm={12} md={8} lg={6} key={`${deal.product_url}-${index}`}>
            <GridCard product={deal} />
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