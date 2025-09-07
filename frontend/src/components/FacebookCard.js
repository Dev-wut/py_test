import React, { useRef, useState } from 'react';
import { Row, Col, Button, Tag, Typography, Space, message, theme } from 'antd';
import { LazyLoadImage } from 'react-lazy-load-image-component';
import { DownloadOutlined, FacebookOutlined, ShoppingCartOutlined, StarFilled, CopyOutlined, EditOutlined, LinkOutlined } from '@ant-design/icons';
import { getStoreColor } from '../config/storeColors';
import EditDealModal from './EditDealModal';

const { Title, Text } = Typography;

const FacebookCard = ({ product, onDownload, calculateSavings }) => {
  const cardRef = useRef(null);
  const { token } = theme.useToken();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editableProduct, setEditableProduct] = useState(product);

  const showModal = () => {
    setIsModalVisible(true);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
  };

  const handleFinish = async (values, type) => {
    if (type === 'temporary') {
      setEditableProduct({ ...editableProduct, ...values });
      message.success('UI Updated temporarily!');
      setIsModalVisible(false);
    } else {
      try {
        const response = await fetch(`/api/deals/${editableProduct.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(values),
        });
        if (response.ok) {
          setEditableProduct({ ...editableProduct, ...values });
          message.success('Deal updated successfully!');
        } else {
          message.error('Failed to update deal.');
        }
      } catch (error) {
        console.error('Failed to update deal:', error);
        message.error('Failed to update deal.');
      }
      setIsModalVisible(false);
    }
  };

  return (
    <div style={{ position: 'relative' }}>
      <div style={{ position: 'absolute', bottom: '24px', right: '24px', display: 'flex', gap: '8px', zIndex: 2 }}>
        <Button
          className="action-button onrow-button"
          icon={<LinkOutlined />}
          onClick={() => window.open(editableProduct.product_url, '_blank')}
        />
        <Button
          className="action-button edit-button"
          icon={<EditOutlined />}
          onClick={showModal}
        />
        <Button
          className="action-button copy-button"
          icon={<CopyOutlined />}
          onClick={() => {
            navigator.clipboard.writeText(editableProduct.title);
            message.success('Copied title');
          }}
        />
        <Button
          className="action-button download-button"
          icon={<DownloadOutlined />}
          onClick={() => onDownload(cardRef)}
        />
      </div>
      <div
        ref={cardRef}
        style={{
          width: '1200px',
          height: '630px',
          background: 'white',
          borderRadius: token.borderRadius * 1.5,
          boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
          overflow: 'hidden'
        }}
      >
        <Row style={{ height: '100%' }}>
          <Col span={12} style={{ position: 'relative', background: '#fafafa' }}>
            <Tag color={getStoreColor(editableProduct.merchant)} style={{ position: 'absolute', top: '24px', left: '24px', padding: '8px 16px', borderRadius: '16px', fontSize: '16px', fontWeight: 'bold', zIndex: 1 }}>
              {editableProduct.merchant}
            </Tag>
            <Tag
              color={token.colorPrimary}
              style={{ position: 'absolute', top: '24px', right: '24px', padding: '8px 16px', borderRadius: '16px', fontSize: '16px', fontWeight: 'bold', zIndex: 1 }}
            >
              {editableProduct.discount}
            </Tag>
            <LazyLoadImage
              alt={editableProduct.title}
              effect="blur"
              src={`/api/proxy-image?url=${encodeURIComponent(editableProduct.image_url)}`}
              width="100%"
              height="100%"
              style={{ objectFit: 'cover' }}
              onError={(e) => { e.target.src = "https://via.placeholder.com/600x630/e5e7eb/6b7280?text=No+Image"; }}
            />
          </Col>
          <Col span={12} style={{ padding: '32px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <Title level={2} style={{ marginBottom: '24px', lineHeight: 1.3, maxHeight: '150px', overflow: 'hidden' }}>{editableProduct.title}</Title>
              {editableProduct.rating && parseFloat(editableProduct.rating.split('/')[0]) > 0 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                  {[...Array(5)].map((_, i) => (
                    <StarFilled
                      key={i}
                      style={{
                        color: i < parseFloat(editableProduct.rating.split('/')[0]) ? '#FFD700' : '#e0e0e0',
                        fontSize: '20px'
                      }}
                    />
                  ))}
                  <Text style={{ fontSize: '18px', color: '#555' }}>{editableProduct.rating} ({editableProduct.reviews_count})</Text>
                </div>
              )}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <Title level={1} style={{ margin: 0, color: token.colorPrimary }}>฿{editableProduct.price}</Title>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <Text delete style={{ fontSize: '24px' }}>฿{editableProduct.original_price}</Text>
                <Tag
                  color={token.colorPrimaryBg}
                  style={{ color: token.colorPrimary, padding: '8px 12px', borderRadius: '8px', fontSize: '18px', fontWeight: 'bold' }}
                >
                  ประหยัด ฿{calculateSavings(editableProduct.original_price, editableProduct.price)}
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
      <EditDealModal
        visible={isModalVisible}
        onCancel={handleCancel}
        onFinish={handleFinish}
        initialValues={editableProduct}
      />
    </div>
  );
};

export default FacebookCard;
