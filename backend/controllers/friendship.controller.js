import Friendship from '../models/friendship.model.js';
import User from '../models/user.model.js';
import mongoose from 'mongoose';

export const getFriends = async (req, res) => {
  const userId = req.user._id;
  try {
    const friendsDetails = await Friendship.aggregate([
      {
        $match: {
          $or: [{ userId: userId }, { friendId: userId }],
          status: true,
        },
      },
      {
        $lookup: {
          from: 'users', // The 'users' collection
          let: { userId: '$userId', friendId: '$friendId' },
          pipeline: [
            {
              $match: {
                $expr: {
                  $or: [{ $eq: ['$_id', '$$userId'] }, { $eq: ['$_id', '$$friendId'] }],
                },
              },
            },
            {
              $match: { _id: { $ne: userId } },
            },
            {
              $project: { _id: 1, username: 1, fullName: 1, gender: 1, profilePicture: 1 }, // Project specific fields you need
            },
          ],
          as: 'friendDetails',
        },
      },
      { $unwind: '$friendDetails' },
      { $replaceRoot: { newRoot: '$friendDetails' } }, // Replace the root with the friend details
    ]);

    res.status(201).json(friendsDetails); // Return the array of friend details directly
  } catch (err) {
    res.status(500).json({ message: 'Internal Server Error', error: err.message });
    throw err;
  }
};

export const reqFriend = async (req, res) => {
  const userId = req.user._id;
  const { friendId } = req.body;

  if (!mongoose.Types.ObjectId.isValid(userId) || !mongoose.Types.ObjectId.isValid(friendId)) {
    return res.status(400).json({ message: 'Invalid user ID or friend ID' });
  }

  try {
    // Check if the friendship already existsj
    const existingFriendship = await Friendship.findOne({
      $or: [
        { userId, friendId },
        { userId: friendId, friendId: userId },
      ],
    });

    if (existingFriendship) {
      return res.status(400).json({ message: 'Friend request already exists or you are already friends' });
    }

    const friendship = new Friendship({
      userId,
      friendId,
      status: false, // pending request
    });

    await friendship.save();

    res.status(201).json({ message: 'Friend request sent successfully', friendship });
  } catch (err) {
    res.status(500).json({ message: 'Internal server error', error: err.message });
  }
};

export const addFriend = async (req, res) => {
  const userId = req.user._id;
  const { friendId } = req.body;

  if (!mongoose.Types.ObjectId.isValid(userId) || !mongoose.Types.ObjectId.isValid(friendId)) {
    return res.status(400).json({ message: 'Invalid user ID or friend ID' });
  }

  try {
    // Check if the friendship request exists and is pending
    const friendship = await Friendship.findOne({
      $or: [
        { userId, friendId },
        { userId: friendId, friendId: userId },
      ],
      status: false, // Pending request
    });

    if (!friendship) {
      return res.status(404).json({ message: 'Friend request not found or already accepted' });
    }

    // Update the status to true
    friendship.status = true;
    await friendship.save();

    res.status(200).json({ message: 'Friend request accepted successfully', friendship });
  } catch (err) {
    res.status(500).json({ message: 'Internal server error', error: err.message });
  }
};

export const rejectFriend = async (req, res) => {
  const userId = req.user._id;
  const { friendId } = req.body;

  if (!mongoose.Types.ObjectId.isValid(userId) || !mongoose.Types.ObjectId.isValid(friendId)) {
    return res.status(400).json({ message: 'Invalid user ID or friend ID' });
  }

  try {
    // Check if the friendship request exists and is pending
    const friendship = await Friendship.findOneAndDelete({
      $or: [
        { userId, friendId },
        { userId: friendId, friendId: userId },
      ],
      status: false, // Pending request
    });

    if (!friendship) {
      return res.status(404).json({ message: 'Friend request not found or already processed' });
    }

    res.status(200).json({ message: 'Friend request rejected successfully' });
  } catch (err) {
    res.status(500).json({ message: 'Internal server error', error: err.message });
  }
};

export const searchFriend = async (req, res) => {
  try {
    const { keyword } = req.query;
    // Get the logged-in user's ID
    const loggedInUserId = req.user._id;

    if (!keyword) {
      return res.status(400).json({ message: 'Keyword is required' });
    }

    // Create a case-insensitive regular expression for the keyword
    const regex = new RegExp(keyword, 'i');

    // Search for users whose name matches the keyword
    let friends = await User.find({
      $or: [{ fullName: { $regex: regex } }, { username: { $regex: regex } }],
      _id: { $ne: loggedInUserId },
    }).select('_id fullName username gender profilePicture');

    // Get the list of friends for the logged-in user
    const friendships = await Friendship.find({
      $or: [{ userId: loggedInUserId }, { friendId: loggedInUserId }],
    });

    // Create a set of friend IDs
    const friendIds = new Set(friendships.map((f) => (f.userId.equals(loggedInUserId) ? f.friendId.toString() : f.userId.toString())));

    // Filter out users who are already friends
    friends = friends.filter((f) => !friendIds.has(f._id.toString()));

    res.status(200).json(friends);
  } catch (error) {
    console.log('Error in searchFriend controller: ', error.message);
    res.status(500).json({ message: error.message });
  }
};

export const getRequestFriendship = async (req, res) => {
  // Get the logged-in user's ID
  const userId = req.user._id;

  try {
    const pendingRequests = await Friendship.find({
      friendId: userId, // Logged in user is the friendId
      status: false,
    }).populate('userId', 'username fullName profilePicture'); // Adjust fields to populate as needed

    // Filter to only include user info
    const users = pendingRequests.map((request) => {
      return request.userId;
    });
    res.json(users);
  } catch (error) {
    console.error('Error fetching friend requests:', error);
    res.status(500).json({ error: 'Failed to fetch friend requests' });
  }
};
