import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Typography, message, Card, Row, Col } from 'antd';
import axios from 'axios';

const { Title, Text } = Typography;
const { TextArea } = Input;

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

const ScraperCriteria = () => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchConfig = async () => {
            setLoading(true);
            try {
                const response = await axios.get(`${API_BASE_URL}/api/scraper_config`);
                const config = response.data;
                // Transform 'class' to 'class_name' for form fields
                const transformedSelectors = {};
                for (const key in config.selectors) {
                    const selector = config.selectors[key];
                    transformedSelectors[key] = {
                        ...selector,
                        class_name: selector.class, // Map 'class' to 'class_name'
                    };
                    if (selector.attrs && typeof selector.attrs === 'object') {
                        transformedSelectors[key].attrs = JSON.stringify(selector.attrs);
                    }
                    delete transformedSelectors[key].class; // Remove original 'class' key
                }
                const transformedConfig = {
                    ...config,
                    selectors: transformedSelectors,
                };
                form.setFieldsValue(transformedConfig);
            } catch (error) {
                message.error('Failed to fetch scraper configuration.');
                console.error('Error fetching config:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchConfig();
    }, [form]);

    const onFinish = async (values) => {
        setLoading(true);
        try {
            // Reconstruct nested objects for API
            const configToSend = {
                base_url: values.base_url,
                selectors: values.selectors,
                json_keys: values.json_keys,
            };

            // Parse attrs JSON string back to object and rename class_name -> class
            for (const key in configToSend.selectors) {
                const selector = configToSend.selectors[key];
                if (selector.attrs && typeof selector.attrs === 'string') {
                    try {
                        selector.attrs = JSON.parse(selector.attrs);
                    } catch (e) {
                        message.error(`Invalid JSON in ${key} Attrs: ${e.message}`);
                        setLoading(false);
                        return; // Stop submission
                    }
                }
                if (Object.prototype.hasOwnProperty.call(selector, 'class_name')) {
                    selector.class = selector.class_name;
                    delete selector.class_name;
                }
            }

            await axios.post(`${API_BASE_URL}/api/scraper_config`, configToSend);
            message.success('Scraper configuration updated successfully!');
        } catch (error) {
            message.error('Failed to update scraper configuration.');
            console.error('Error updating config:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '24px' }}>
            <Title level={2}>Scraper Configuration</Title>
            <Text type="secondary">Adjust the URL, HTML selectors, and JSON keys used by the scraper.</Text>
            <Form
                form={form}
                layout="vertical"
                onFinish={onFinish}
                initialValues={{
                    base_url: '',
                    selectors: {
                        load_more_button: { tag: '', class_name: '', id: '', attrs: '' },
                        hot_deals_container: { tag: '', class_name: '', id: '', attrs: '' },
                        product_item: { tag: '', class_name: '', id: '', attrs: '' },
                        title: { tag: '', class_name: '', id: '', attrs: '' },
                        original_price: { tag: '', class_name: '', id: '', attrs: '' },
                        price: { tag: '', class_name: '', id: '', attrs: '' },
                        discount: { tag: '', class_name: '', id: '', attrs: '' },
                        image: { tag: '', class_name: '', id: '', attrs: '' },
                        merchant_image: { tag: '', class_name: '', id: '', attrs: '' },
                        product_link: { tag: '', class_name: '', id: '', attrs: '' },
                        rating: { tag: '', class_name: '', id: '', attrs: '' },
                    },
                    json_keys: {
                        title: '',
                        price: '',
                        original_price: '',
                        discount: '',
                        image_url: '',
                        product_url: '',
                        merchant: '',
                        merchant_image: '',
                        rating: '',
                        reviews_count: '',
                    },
                }}
                style={{ marginTop: '24px' }}
            >
                <Card title="General Settings" style={{ marginBottom: '24px' }}>
                    <Form.Item label="Base URL" name="base_url" rules={[{ required: true, message: 'Please input the base URL!' }]}>
                        <Input />
                    </Form.Item>
                </Card>

                <Card title="HTML Selectors" style={{ marginBottom: '24px' }}>
                    <Card type="inner" title="Page Navigation & Structure" style={{ marginBottom: '16px' }}>
                        <Form.Item label="Load More Button Class" name={['selectors', 'load_more_button', 'class_name']}>
                            <Input placeholder="Class Name" />
                        </Form.Item>
                        <Form.Item label="Hot Deals Container Tag" name={['selectors', 'hot_deals_container', 'tag']}>
                            <Input placeholder="Tag (e.g., div)" />
                        </Form.Item>
                        <Form.Item label="Hot Deals Container Class" name={['selectors', 'hot_deals_container', 'class_name']}>
                            <Input placeholder="Class Name" />
                        </Form.Item>
                        <Form.Item label="Hot Deals Container ID" name={['selectors', 'hot_deals_container', 'id']}>
                            <Input placeholder="ID" />
                        </Form.Item>
                        <Form.Item label="Product Item Tag" name={['selectors', 'product_item', 'tag']}>
                            <Input placeholder="Tag (e.g., div)" />
                        </Form.Item>
                        <Form.Item label="Product Item Class" name={['selectors', 'product_item', 'class_name']}>
                            <Input placeholder="Class Name" />
                        </Form.Item>
                    </Card>

                    <Card type="inner" title="Product Text Elements" style={{ marginBottom: '16px' }}>
                        <Form.Item label="Title Tag" name={['selectors', 'title', 'tag']}>
                            <Input placeholder="Tag (e.g., h3)" />
                        </Form.Item>
                        <Form.Item label="Title Class" name={['selectors', 'title', 'class_name']}>
                            <Input placeholder="Class Name" />
                        </Form.Item>
                        <Form.Item label="Original Price Tag" name={['selectors', 'original_price', 'tag']}>
                            <Input placeholder="Tag (e.g., del)" />
                        </Form.Item>
                        <Form.Item label="Original Price Class" name={['selectors', 'original_price', 'class_name']}>
                            <Input placeholder="Class Name" />
                        </Form.Item>
                        <Form.Item label="Price Tag" name={['selectors', 'price', 'tag']}>
                            <Input placeholder="Tag (e.g., span)" />
                        </Form.Item>
                        <Form.Item label="Price Class" name={['selectors', 'price', 'class_name']}>
                            <Input placeholder="Class Name" />
                        </Form.Item>
                        <Form.Item label="Discount Tag" name={['selectors', 'discount', 'tag']}>
                            <Input placeholder="Tag (e.g., div)" />
                        </Form.Item>
                        <Form.Item label="Discount Class" name={['selectors', 'discount', 'class_name']}>
                            <Input placeholder="Class Name" />
                        </Form.Item>
                    </Card>

                    <Card type="inner" title="Product Image Elements" style={{ marginBottom: '16px' }}>
                        <Form.Item label="Image Tag" name={['selectors', 'image', 'tag']}>
                            <Input placeholder="Tag (e.g., img)" />
                        </Form.Item>
                        <Form.Item label="Image Class" name={['selectors', 'image', 'class_name']}>
                            <Input placeholder="Class Name" />
                        </Form.Item>
                        <Form.Item label="Merchant Image Tag" name={['selectors', 'merchant_image', 'tag']}>
                            <Input placeholder="Tag (e.g., img)" />
                        </Form.Item>
                        <Form.Item label="Merchant Image Class" name={['selectors', 'merchant_image', 'class_name']}>
                            <Input placeholder="Class Name" />
                        </Form.Item>
                    </Card>

                    <Card type="inner" title="Product Link & Rating Elements">
                        <Form.Item label="Product Link Tag" name={['selectors', 'product_link', 'tag']}>
                            <Input placeholder="Tag (e.g., a)" />
                        </Form.Item>
                        <Form.Item label="Product Link Attrs (JSON)" name={['selectors', 'product_link', 'attrs']}>
                            <TextArea placeholder='{"href": true, "onmousedown": true}' autoSize={{ minRows: 1, maxRows: 3 }} />
                        </Form.Item>
                        <Form.Item label="Rating Tag" name={['selectors', 'rating', 'tag']}>
                            <Input placeholder="Tag (e.g., div)" />
                        </Form.Item>
                        <Form.Item label="Rating Class" name={['selectors', 'rating', 'class_name']}>
                            <Input placeholder="Class Name" />
                        </Form.Item>
                    </Card>
                </Card>

                <Card title="JSON Output Keys">
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item label="Title Key" name={['json_keys', 'title']}>
                                <Input />
                            </Form.Item>
                            <Form.Item label="Price Key" name={['json_keys', 'price']}>
                                <Input />
                            </Form.Item>
                            <Form.Item label="Original Price Key" name={['json_keys', 'original_price']}>
                                <Input />
                            </Form.Item>
                            <Form.Item label="Discount Key" name={['json_keys', 'discount']}>
                                <Input />
                            </Form.Item>
                            <Form.Item label="Image URL Key" name={['json_keys', 'image_url']}>
                                <Input />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item label="Product URL Key" name={['json_keys', 'product_url']}>
                                <Input />
                            </Form.Item>
                            <Form.Item label="Merchant Key" name={['json_keys', 'merchant']}>
                                <Input />
                            </Form.Item>
                            <Form.Item label="Merchant Image Key" name={['json_keys', 'merchant_image']}>
                                <Input />
                            </Form.Item>
                            <Form.Item label="Rating Key" name={['json_keys', 'rating']}>
                                <Input />
                            </Form.Item>
                            <Form.Item label="Reviews Count Key" name={['json_keys', 'reviews_count']}>
                                <Input />
                            </Form.Item>
                        </Col>
                    </Row>
                </Card>

                <Form.Item style={{ marginTop: '24px', textAlign: 'right' }}>
                    <Button type="primary" htmlType="submit" loading={loading}>
                        Save Configuration
                    </Button>
                </Form.Item>
            </Form>
        </div>
    );
};

export default ScraperCriteria;