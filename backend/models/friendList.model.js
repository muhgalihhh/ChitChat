import mongoose from 'mongoose';

const friendListSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
    friendId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
    status: {
      type: Boolean,
      required: true,
      default: false,
    },
    // Create at, Update at => message.createdAAt : 15.30
  },
  { timestamps: true }
);

const FriendList = mongoose.model('FriendList', friendListSchema);

export default FriendList;
