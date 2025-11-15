import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { consultsAPI } from '../services/api';
import type { ConsultRequest, ConsultComment } from '../types';

const ConsultDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [consult, setConsult] = useState<ConsultRequest | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [commentText, setCommentText] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);
  const [updatingStatus, setUpdatingStatus] = useState(false);

  useEffect(() => {
    if (id) {
      loadConsult();
    }
  }, [id]);

  const loadConsult = async () => {
    setLoading(true);
    try {
      const data = await consultsAPI.get(parseInt(id!));
      setConsult(data);
    } catch (err: any) {
      setError('Failed to load consult details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!commentText.trim() || !id) return;

    setSubmittingComment(true);
    try {
      await consultsAPI.addComment(parseInt(id), commentText);
      setCommentText('');
      await loadConsult(); // Reload to get updated comments
    } catch (err: any) {
      alert('Failed to add comment');
      console.error(err);
    } finally {
      setSubmittingComment(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!id) return;

    setUpdatingStatus(true);
    try {
      await consultsAPI.updateStatus(parseInt(id), newStatus);
      await loadConsult(); // Reload to get updated status
    } catch (err: any) {
      alert('Failed to update status');
      console.error(err);
    } finally {
      setUpdatingStatus(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'stat':
        return 'bg-red-100 text-red-800';
      case 'urgent':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-green-100 text-green-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-purple-100 text-purple-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (error || !consult) {
    return (
      <div className="min-h-screen bg-gray-100">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error || 'Consult not found'}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center">
            <button
              onClick={() => navigate('/dashboard')}
              className="mr-4 text-gray-600 hover:text-gray-900"
            >
              ← Back
            </button>
            <h1 className="text-2xl font-bold text-gray-900">
              Consultation #{consult.id}
            </h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Consult Info */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">
                    {consult.from_department_name} → {consult.to_department_name}
                  </h2>
                  <p className="text-sm text-gray-500 mt-1">
                    Requested by {consult.requested_by_name} on{' '}
                    {new Date(consult.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex space-x-2">
                  <span
                    className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getPriorityColor(
                      consult.priority
                    )}`}
                  >
                    {consult.priority.toUpperCase()}
                  </span>
                  <span
                    className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(
                      consult.status
                    )}`}
                  >
                    {consult.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-700">Clinical Summary</h3>
                  <p className="mt-1 text-sm text-gray-900 whitespace-pre-wrap">
                    {consult.clinical_summary}
                  </p>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-gray-700">Consultation Question</h3>
                  <p className="mt-1 text-sm text-gray-900 whitespace-pre-wrap">
                    {consult.consult_question}
                  </p>
                </div>
              </div>
            </div>

            {/* Comments Section */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Comments & Replies ({consult.comments.length})
              </h2>

              {/* Comments List */}
              <div className="space-y-4 mb-6">
                {consult.comments.length === 0 ? (
                  <p className="text-gray-500 text-sm">No comments yet</p>
                ) : (
                  consult.comments.map((comment: ConsultComment) => (
                    <div key={comment.id} className="border-l-4 border-blue-500 pl-4 py-2">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {comment.author_name || comment.author_username}
                          </p>
                          <p className="text-xs text-gray-500">
                            {new Date(comment.created_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <p className="mt-2 text-sm text-gray-700 whitespace-pre-wrap">
                        {comment.message}
                      </p>
                    </div>
                  ))
                )}
              </div>

              {/* Add Comment Form */}
              <form onSubmit={handleAddComment} className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Add a comment
                </label>
                <textarea
                  value={commentText}
                  onChange={(e) => setCommentText(e.target.value)}
                  rows={3}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter your comment..."
                />
                <button
                  type="submit"
                  disabled={submittingComment || !commentText.trim()}
                  className="mt-2 px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400"
                >
                  {submittingComment ? 'Adding...' : 'Add Comment'}
                </button>
              </form>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Patient Info */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Patient Information</h2>
              <dl className="space-y-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Name</dt>
                  <dd className="text-sm text-gray-900">{consult.patient_details.name}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Hospital ID</dt>
                  <dd className="text-sm text-gray-900">{consult.patient_details.hospital_id}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Age</dt>
                  <dd className="text-sm text-gray-900">{consult.patient_details.age}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Gender</dt>
                  <dd className="text-sm text-gray-900">
                    {consult.patient_details.gender === 'M'
                      ? 'Male'
                      : consult.patient_details.gender === 'F'
                      ? 'Female'
                      : 'Other'}
                  </dd>
                </div>
                {consult.patient_details.bed_ward_info && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Bed/Ward</dt>
                    <dd className="text-sm text-gray-900">
                      {consult.patient_details.bed_ward_info}
                    </dd>
                  </div>
                )}
              </dl>
            </div>

            {/* Status Update */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Update Status</h2>
              <div className="space-y-2">
                {['pending', 'in_progress', 'completed', 'cancelled'].map((status) => (
                  <button
                    key={status}
                    onClick={() => handleStatusChange(status)}
                    disabled={updatingStatus || consult.status === status}
                    className={`w-full px-4 py-2 text-sm font-medium rounded-md ${
                      consult.status === status
                        ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                        : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {status.replace('_', ' ').toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ConsultDetailPage;
