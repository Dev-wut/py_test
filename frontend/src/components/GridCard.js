import React, { useRef } from 'react';
import { Card, Tag, Typography, Button, message, theme } from 'antd';
import { LazyLoadImage } from 'react-lazy-load-image-component';
import { DownloadOutlined, StarFilled, CopyOutlined } from '@ant-design/icons';
import { getStoreColor } from '../config/storeColors';

const { Paragraph, Title, Text } = Typography;

const GridCard = ({ product, onDownload, calculateSavings }) => {
  const cardRef = useRef(null);
  const { token } = theme.useToken();
  return (
    <div style={{ position: 'relative', height: '100%' }}>
      <div
        style={{
          position: 'absolute',
          top: '12px',
          right: '12px',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
          zIndex: 2
        }}
      >
        <Button
          className="action-button copy-button"
          icon={<CopyOutlined />}
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            navigator.clipboard.writeText(product.title);
            message.success('Copied title');
          }}
        />
        <Button
          className="action-button download-button"
          icon={<DownloadOutlined />}
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); onDownload(cardRef); }}
        />
      </div>
      <div ref={cardRef} style={{ height: '100%' }}>
        <a href={product.product_url} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none', height: '100%', display: 'block' }}>
          <Card
            hoverable
            style={{ overflow: 'hidden', height: '100%' }}
            cover={
              <div style={{ position: 'relative', height: '180px', background: '#f5f5f5' }}>
                <div
                  style={{
                    position: 'absolute',
                    top: '12px',
                    left: '12px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '4px',
                    zIndex: 1
                  }}
                >
                    {product.merchant ? (
                      <Tag
                        color={getStoreColor(product.merchant)}
                        style={{ borderRadius: '9999px', fontSize: '10px', fontWeight: 'bold' }}
                      >
                        {product.merchant}
                      </Tag>
                    ) : null}
                  <Tag
                    color={token.colorPrimary}
                    style={{ borderRadius: '9999px', fontSize: '10px', fontWeight: 'bold' }}
                  >
                    {product.discount}
                  </Tag>
                </div>
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
              {product.rating && parseFloat(product.rating.split('/')[0]) > 0 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '8px' }}>
                  {[...Array(5)].map((_, i) => (
                    <StarFilled
                      key={i}
                      style={{
                        color: i < parseFloat(product.rating.split('/')[0]) ? '#FFD700' : '#e0e0e0',
                        fontSize: '14px'
                      }}
                    />
                  ))}
                  <Text style={{ fontSize: '12px', color: '#555' }}>{product.rating} ({product.reviews_count})</Text>
                </div>
              )}
              <div style={{ margin: '12px 0' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Title level={5} style={{ margin: 0, color: token.colorPrimary }}>฿{product.price}</Title>
                  <Tag
                    color={token.colorPrimaryBg}
                    style={{ color: token.colorPrimary, fontSize: '10px', fontWeight: 'semibold', borderRadius: '4px' }}
                  >
                    ประหยัด ฿{calculateSavings(product.original_price, product.price)}
                  </Tag>
                </div>
                <Text delete type="secondary" style={{ fontSize: '12px' }}>฿{product.original_price}</Text>
              </div>
            </div>
            <div
              style={{
                background: 'linear-gradient(to right, #4A90E2, #9013FE)',
                color: 'white',
                padding: '8px',
                textAlign: 'center',
                borderRadius: token.borderRadius,
                marginTop: 'auto'
              }}
            >
              <Text style={{ color: 'white', fontSize: '12px', fontWeight: 'medium' }}>
                โปรดีบอกต่อ Prod
              </Text>
            </div>
          </Card>
        </a>
      </div>
    </div>
  );
};

export default GridCard;
