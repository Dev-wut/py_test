import React, { useRef } from 'react';
import { Row, Col, Button, Tag, Typography, Space } from 'antd';
import { LazyLoadImage } from 'react-lazy-load-image-component';
import { DownloadOutlined, FacebookOutlined, ShoppingCartOutlined, StarFilled } from '@ant-design/icons';
import { getStoreColor } from '../config/storeColors';

const { Title, Text } = Typography;

const FacebookCard = ({ product, onDownload, calculateSavings }) => {
  const cardRef = useRef(null);
  return (
    <div style={{ position: 'relative' }}>
      <Button
        className="download-button"
        icon={<DownloadOutlined />}
        onClick={() => onDownload(cardRef)}
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
              {product.rating && parseFloat(product.rating.split('/')[0]) > 0 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                  {[...Array(5)].map((_, i) => (
                    <StarFilled
                      key={i}
                      style={{
                        color: i < parseFloat(product.rating.split('/')[0]) ? '#FFD700' : '#e0e0e0',
                        fontSize: '20px'
                      }}
                    />
                  ))}
                  <Text style={{ fontSize: '18px', color: '#555' }}>{product.rating} ({product.reviews_count})</Text>
                </div>
              )}
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
  );
};

export default FacebookCard;
