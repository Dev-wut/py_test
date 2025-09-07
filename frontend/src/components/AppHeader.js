import React from 'react';
import { Layout, Row, Col, Statistic, Button, Space, Typography } from 'antd';
import { SyncOutlined } from '@ant-design/icons';
import AppLogo from './AppLogo';

const { Header } = Layout;
const { Text } = Typography;

const AppHeader = ({ totalProducts, loading, onRefresh, pageType }) => (
  <Header className="app-header" style={{ background: '#001529' }}>
    <div className="header-container" style={{height: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
      <AppLogo />
      <div className="statistic-container-mobile-hide" style={{ flexGrow: 1, textAlign: 'center' }}>
        <Statistic
          title={<Text style={{color: '#a6adb4'}}>{pageType === 'owner' ? 'Owner Deals Found' : 'Deals Found'}</Text>}
          value={totalProducts}
          valueStyle={{color: '#fff'}}
        />
      </div>
      <Space align="center" size="small" wrap>
        <Row className="header-buttons-row" gutter={[8, 8]} style={{ flexGrow: 1, justifyContent: 'flex-end' }}>
          {pageType !== 'owner' && (
            <>
              <Col xs={24} sm={12} md={8} lg={8} xl={8}>
                <Button type="default" ghost onClick={() => window.open('/scraper-criteria', '_blank')} style={{ width: '100%' }}>
                  Scraper Config
                </Button>
              </Col>
              <Col xs={24} sm={12} md={8} lg={8} xl={8}>
                <Button type="default" ghost onClick={() => window.open('/owner-product', '_blank')} style={{ width: '100%' }}>
                  Create Facebook Card
                </Button>
              </Col>
              <Col xs={24} sm={12} md={8} lg={8} xl={8}>
                <Button type="primary" ghost icon={<SyncOutlined />} onClick={onRefresh} loading={loading} style={{ width: '100%' }}>
                  Refresh
                </Button>
              </Col>
            </>
          )}
          {pageType === 'owner' && (
            <Col>
              <Text style={{color: 'white', fontSize: '1.2rem'}}>Owner Product</Text>
            </Col>
          )}
        </Row>
      </Space>
    </div>
  </Header>
);

export default AppHeader;
