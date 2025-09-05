import React from 'react';
import { Pagination } from 'antd';

const PaginationControls = ({ currentPage, totalProducts, pageSize, onPageChange }) => (
  <div style={{ display: 'flex', justifyContent: 'center', marginTop: '24px' }}>
    <Pagination
      current={currentPage}
      total={totalProducts}
      pageSize={pageSize}
      onChange={onPageChange}
      showSizeChanger={false}
    />
  </div>
);

export default PaginationControls;
