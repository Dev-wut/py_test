import React, { useEffect } from 'react';
import { Modal, Form, Input, Button, Row, Col } from 'antd';

const EditDealModal = ({ visible, onCancel, onFinish, onDelete, initialValues }) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (initialValues) {
      form.setFieldsValue(initialValues);
    }
  }, [initialValues, form]);

  const handleOk = () => {
    form
      .validateFields()
      .then(values => {
        form.resetFields();
        onFinish(values);
      })
      .catch(info => {
        console.log('Validate Failed:', info);
      });
  };

  const handleDelete = () => {
    onDelete();
  };

  const handleValuesChange = (changedValues, allValues) => {
    if (changedValues.price || changedValues.original_price) {
      const { price, original_price } = allValues;
      if (price && original_price) {
        const priceNum = parseFloat(String(price).replace(/,/g, ''));
        const originalPriceNum = parseFloat(String(original_price).replace(/,/g, ''));
        if (!isNaN(priceNum) && !isNaN(originalPriceNum) && originalPriceNum > 0) {
          const discountPercent = ((originalPriceNum - priceNum) / originalPriceNum) * 100;
          form.setFieldsValue({ discount: `${discountPercent.toFixed(0)}%` });
        }
      }
    }
  };

  return (
    <Modal
      visible={visible}
      title="Edit Deal"
      okText="Save"
      cancelText="Cancel"
      onCancel={onCancel}
      onOk={handleOk}
      width="90vw"
      style={{ top: 20 }}
      footer={[
        <Button key="delete" danger onClick={handleDelete}>
          Delete
        </Button>,
        <Button key="back" onClick={onCancel}>
          Cancel
        </Button>,
        <Button key="submit" type="primary" onClick={handleOk}>
          Save
        </Button>,
      ]}
    >
      <Form
        form={form}
        layout="vertical"
        name="form_in_modal"
        initialValues={initialValues}
        onValuesChange={handleValuesChange}
      >
        <Row gutter={16}>
          <Col span={24}>
            <Form.Item
              name="title"
              label="Title"
              rules={[{ required: true, message: 'Please input the title of the deal!' }]}
            >
              <Input />
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="price" label="Price">
              <Input type="number" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="original_price" label="Original Price" rules={[{ required: true, message: 'Please input the original price!' }]}>
              <Input type="number" />
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="discount" label="Discount">
              <Input />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="image_url" label="Image URL" rules={[{ required: true, message: 'Please input the image URL!' }]}>
              <Input />
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="product_url" label="Product URL">
              <Input />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="merchant" label="Merchant">
              <Input />
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="merchant_image" label="Merchant Image URL">
              <Input />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="rating" label="Rating (e.g., 4.5/5)">
              <Input />
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="reviews_count" label="Reviews Count">
              <Input />
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Modal>
  );
};

export default EditDealModal;
