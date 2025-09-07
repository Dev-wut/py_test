import React from 'react';
import { Modal, Form, Input, Button } from 'antd';

const EditDealModal = ({ visible, onCancel, onFinish, initialValues }) => {
  const [form] = Form.useForm();

  const handleOk = () => {
    form
      .validateFields()
      .then(values => {
        form.resetFields();
        onFinish(values, 'permanent');
      })
      .catch(info => {
        console.log('Validate Failed:', info);
      });
  };

  const handleTemporarySave = () => {
    form
      .validateFields()
      .then(values => {
        onFinish(values, 'temporary');
      })
      .catch(info => {
        console.log('Validate Failed:', info);
      });
  };

  return (
    <Modal
      visible={visible}
      title="Edit Deal"
      okText="Permanent Save"
      cancelText="Cancel"
      onCancel={onCancel}
      onOk={handleOk}
      footer={[
        <Button key="back" onClick={onCancel}>
          Cancel
        </Button>,
        <Button key="temporary" onClick={handleTemporarySave}>
          Temporary Save
        </Button>,
        <Button key="submit" type="primary" onClick={handleOk}>
          Permanent Save
        </Button>,
      ]}
    >
      <Form
        form={form}
        layout="vertical"
        name="form_in_modal"
        initialValues={initialValues}
      >
        <Form.Item
          name="title"
          label="Title"
          rules={[{ required: true, message: 'Please input the title of the deal!' }]}
        >
          <Input />
        </Form.Item>
        <Form.Item
          name="price"
          label="Price"
        >
          <Input />
        </Form.Item>
        <Form.Item
          name="original_price"
          label="Original Price"
        >
          <Input />
        </Form.Item>
        <Form.Item
          name="discount"
          label="Discount"
        >
          <Input />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default EditDealModal;
