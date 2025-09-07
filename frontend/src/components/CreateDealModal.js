import React from 'react';
import { Modal, Form, Input, Button, message } from 'antd';

const CreateDealModal = ({ visible, onCancel, onFinish }) => {
  const [form] = Form.useForm();

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
      title="Create a New Deal"
      okText="Create"
      cancelText="Cancel"
      onCancel={onCancel}
      onOk={handleOk}
    >
      <Form
        form={form}
        layout="vertical"
        name="form_in_modal"
        onValuesChange={handleValuesChange}
      >
        <Form.Item
          name="title"
          label="Title"
          rules={[{ required: true, message: 'Please input the title of the deal!' }]}
        >
          <Input />
        </Form.Item>
        <Form.Item name="price" label="Price">
          <Input type="number" />
        </Form.Item>
        <Form.Item name="original_price" label="Original Price" rules={[{ required: true, message: 'Please input the original price!' }]}>
          <Input type="number" />
        </Form.Item>
        <Form.Item name="discount" label="Discount">
          <Input />
        </Form.Item>
        <Form.Item name="image_url" label="Image URL" rules={[{ required: true, message: 'Please input the image URL!' }]}>
          <Input />
        </Form.Item>
        <Form.Item name="product_url" label="Product URL">
          <Input />
        </Form.Item>
        <Form.Item name="merchant" label="Merchant">
          <Input />
        </Form.Item>
        <Form.Item name="merchant_image" label="Merchant Image URL">
          <Input />
        </Form.Item>
        <Form.Item name="rating" label="Rating (e.g., 4.5/5)">
          <Input />
        </Form.Item>
        <Form.Item name="reviews_count" label="Reviews Count">
          <Input />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default CreateDealModal;
