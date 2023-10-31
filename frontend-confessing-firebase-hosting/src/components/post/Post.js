import React, { useState } from 'react';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import axios from 'axios';
import './Post.css';

function Post() {
    const [confession, setConfession] = useState('');
    const [city, setCity] = useState('');
    const [isUploading, setIsUploading] = useState(false);
    const [uploadError, setUploadError] = useState(null);
    const [uploadSuccess, setUploadSuccess] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Clear any previous messages
        setUploadError(null);
        setUploadSuccess(null);

        // Get the base API URL from .env
        const baseUrl = process.env.REACT_APP_API_URL;

        // Append the specific endpoint
        const apiUrl = `${baseUrl}/addConfession`;

        try {
            setIsUploading(true);

            const response = await axios.post(apiUrl, {
                id: -1,
                confession: String(confession),
                location: String(city),
            });

            // Handle success, reset form, and display success message
            console.log('Submission successful', response);
            setConfession('');
            setCity('');
            setUploadSuccess('Confession added successfully');
        } catch (error) {
            // Handle errors, display error message, and reset uploading state
            console.error('Error submitting form', error);
            setUploadError('Error adding confession');
        } finally {
            setIsUploading(false);
        }
    }

    return (
        <div className="Post">
            <header className="Post-header">
                <Container>
                    <h1 className="mb-4">Make Your Confession Below</h1>

                    <Form onSubmit={handleSubmit}>
                        <Form.Group as={Row} controlId="inputConfession" className="mb-3">
                            <Form.Label column sm={2}>
                                Enter Confession:
                            </Form.Label>
                            <Col sm={10}>
                                <Form.Control
                                    as="textarea"
                                    rows={5}
                                    value={confession}
                                    onChange={(e) => setConfession(e.target.value)}
                                    required
                                />
                            </Col>
                        </Form.Group>

                        <Form.Group as={Row} controlId="city">
                            <Form.Label column sm={2}>
                                Enter city name:
                            </Form.Label>
                            <Col sm={10}>
                                <Form.Control
                                    type="text"
                                    placeholder="Location"
                                    value={city}
                                    onChange={(e) => setCity(e.target.value)}
                                    required
                                />
                            </Col>
                        </Form.Group>

                        <Row className="mb-3">
                            <Col sm={{ span: 10, offset: 2 }}>
                                <Button type="submit" variant="primary" disabled={isUploading} className="confess-button">
                                    {isUploading ? 'Uploading...' : 'Confess'}
                                </Button>
                            </Col>
                        </Row>
                    </Form>

                    {uploadError && <p className="text-danger">{uploadError}</p>}
                    {uploadSuccess && <p className="text-success">{uploadSuccess}</p>}
                </Container>
            </header>
        </div>
    );
}

export default Post;
