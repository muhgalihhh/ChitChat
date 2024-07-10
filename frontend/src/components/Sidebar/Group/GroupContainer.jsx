import React from 'react';

const GroupContainer = () => {
  return (
    <>
      <div className="flex gap-2 items-center rounded-md cursor-pointer flex-col">
        {/* Wrapper div for the search input */}
        {/* search input */}
        <form action="" className="w-full">
          <label className="input input-bordered flex items-center gap-2">
            <input type="text" className="grow" placeholder="Search" />
            <button type="submit">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="h-4 w-4 opacity-70">
                <path fillRule="evenodd" d="M9.965 11.026a5 5 0 1 1 1.06-1.06l2.755 2.754a.75.75 0 1 1-1.06 1.06l-2.755-2.754ZM10.5 7a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Z" clipRule="evenodd" />
              </svg>
            </button>
          </label>
        </form>
        {/* <GroupList /> */}
        {/* Buatkan peringatan bahwa fitur masih dalam pengembangan dengan logo */}

        <div className="card flex-1 p-20 rounded-md flex items-center justify-center border bg-red-700 mt-10 text-white">
          <span class="loading loading-ring loading-lg"></span>
          <h2>Under Development</h2>
        </div>
      </div>
    </>
  );
};

export default GroupContainer;
