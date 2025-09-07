import React, { useState } from 'react';
import { Layout, Button, Row, Col, Spin, Alert, Empty, message, Modal } from 'antd';
import html2canvas from 'html2canvas';
import AppHeader from '../components/AppHeader';
import FacebookCard from '../components/FacebookCard';
import PaginationControls from '../components/PaginationControls';
import CreateDealModal from '../components/CreateDealModal';
import EditDealModal from '../components/EditDealModal';
import useOwnerDeals from '../hooks/useOwnerDeals';
import styles from '../App.module.css';

const { Content, Footer } = Layout;

const OwnerProduct = () => {
  const [isCreateModalVisible, setIsCreateModalVisible] = useState(false);
  const [isEditModalVisible, setIsEditModalVisible] = useState(false);
  const [editingDeal, setEditingDeal] = useState(null);
  const [modal, contextHolder] = Modal.useModal();

  const {
    deals,
    loading,
    error,
    currentPage,
    totalProducts,
    pageSize,
    fetchDeals,
  } = useOwnerDeals();

  const showCreateModal = () => {
    setIsCreateModalVisible(true);
  };

  const handleCreateCancel = () => {
    setIsCreateModalVisible(false);
  };

  const handleCreateFinish = async (values) => {
    try {
      const response = await fetch('/api/owner_deals', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });
      if (response.ok) {
        message.success('Deal created successfully!');
        fetchDeals(); // Refresh the list
      } else {
        message.error('Failed to create deal.');
      }
    } catch (error) {
      console.error('Failed to create deal:', error);
      message.error('Failed to create deal.');
    }
    setIsCreateModalVisible(false);
  };

  const showEditModal = (deal) => {
    setEditingDeal(deal);
    setIsEditModalVisible(true);
  };

  const handleEditCancel = () => {
    setIsEditModalVisible(false);
    setEditingDeal(null);
  };

  const handleEditFinish = async (values) => {
    if (!editingDeal) return;
    try {
      const response = await fetch(`/api/owner_deals/${editingDeal.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });
      if (response.ok) {
        message.success('Deal updated successfully!');
        fetchDeals(); // Refresh the list
      } else {
        message.error('Failed to update deal.');
      }
    } catch (error) {
      console.error('Failed to update deal:', error);
      message.error('Failed to update deal.');
    }
    setIsEditModalVisible(false);
    setEditingDeal(null);
  };

  const handleDelete = (deal) => {
    modal.confirm({
      title: 'Are you sure you want to delete this deal?',
      content: deal.title,
      okText: 'Yes',
      okType: 'danger',
      cancelText: 'No',
      onOk: async () => {
        try {
          const response = await fetch(`/api/owner_deals/${deal.id}`, {
            method: 'DELETE',
          });
          if (response.ok) {
            message.success('Deal deleted successfully!');
            fetchDeals(); // Refresh the list
          } else {
            message.error('Failed to delete deal.');
          }
        } catch (error) {
          console.error('Failed to delete deal:', error);
          message.error('Failed to delete deal.');
        }
      },
    });
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
      const actionButtons = cardRef.current.parentElement.querySelectorAll('.action-button');
      actionButtons.forEach((btn) => {
        btn.style.display = 'none';
      });

      const canvas = await html2canvas(cardRef.current, {
        backgroundColor: null,
        useCORS: true,
        allowTaint: false,
        scale: 2,
      });

      actionButtons.forEach((btn) => {
        btn.style.display = 'block';
      });

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
        <div className={styles.loadingSpinnerContainer}>
          <Spin size="large" tip="Loading Deals..." />
        </div>
      );
    }

    if (error) {
      return <Alert message="Error" description={error} type="error" showIcon />;
    }

    if (deals.length === 0) {
      return <Empty description="No owner deals found." />;
    }

    return (
      <div className={styles.facebookContainer}>
        {deals.map((deal, index) => (
          <FacebookCard
            product={deal}
            key={index}
            calculateSavings={calculateSavings}
            onEdit={showEditModal}
            onDelete={handleDelete}
            onDownload={handleDownload}
          />
        ))}
      </div>
    );
  };

  return (
    <Layout className={styles.layout}>
      {contextHolder}
      <AppHeader totalProducts={totalProducts} loading={loading} onRefresh={fetchDeals} pageType="owner" />
      <Content className={styles.content}>
        <div style={{ marginBottom: 16 }}>
          <Button type="primary" onClick={showCreateModal}>
            เพิ่มใหม่
          </Button>
        </div>
        <div className={styles.cardListContainer}>{renderContent()}</div>
        <PaginationControls
          currentPage={currentPage}
          totalProducts={totalProducts}
          pageSize={pageSize}
          onPageChange={fetchDeals}
        />
      </Content>
      <Footer className={styles.footer}>
        PriceZA Scraper ©2025 Created with Gemini
      </Footer>
      <CreateDealModal
        visible={isCreateModalVisible}
        onCancel={handleCreateCancel}
        onFinish={handleCreateFinish}
      />
      {editingDeal && (
        <EditDealModal
          visible={isEditModalVisible}
          onCancel={handleEditCancel}
          onFinish={handleEditFinish}
          onDelete={() => handleDelete(editingDeal)}
          initialValues={editingDeal}
        />
      )}
    </Layout>
  );
};

export default OwnerProduct;
