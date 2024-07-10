import useGetConversation from '../../hooks/useGetConversation';
import Conversation from './Conversation';

const ConversationList = () => {
  const { loading, conversation } = useGetConversation();
  console.log('conversation:', conversation);
  return (
    <div className="p-1 flex flex-col w-full">
      {conversation.map((user, idx) => (
        <Conversation key={user._id} conversation={user} lastIdx={idx === conversation.length - 1} />
      ))}
      {loading ? <span className="loading loading-infinity loading-md"></span> : null}
    </div>
  );
};

export default ConversationList;
