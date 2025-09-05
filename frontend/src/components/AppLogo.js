import React from 'react';
import { Typography } from 'antd';
import { ShoppingCartOutlined } from '@ant-design/icons';

const { Title } = Typography;

const AppLogo = () => (
  <div className="logo-container" style={{ display: 'flex', alignItems: 'center', color: 'white' }}>
    <ShoppingCartOutlined style={{ fontSize: '32px' }} />
    <Title level={3} style={{ color: 'white', margin: '0 0 0 12px', whiteSpace: 'nowrap' }}>
      PriceZA Deals Za
    </Title>
  </div>
);

export default AppLogo;
