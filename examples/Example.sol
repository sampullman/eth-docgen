pragma solidity ^0.4.21;

import "./Ownable.sol";

/// @title A contract for testing eth-docgen
/// @author Jane Doe
/// @author John Doe
contract Example is Ownable {
    
    /// The number of things written to storage
    uint public writeCount;

    /// The total amount of funds ever donated to the contract
    uint public donations;

    /// A dummy variable
    bool private dummy = false;

    /// Container for very important things
    struct ImportantThings {
        /// The ID of the container
        uint id;
        /// A mapping of users to their important thing
        mapping(address => string) things;
    }

    /// A list of containers of important things
    ImportantThings[] public thingsList;

    /// A log of writes made to the thingsList
    mapping(address => mapping(uint => uint256)) writeLog;
    
    /// @notice Triggered when a thing is written to storage
    /// @param writer The address of the writer
    /// @param containerId The id of the container the thing was written to
    event WriteEvent(address indexed writer, uint containerId);

    /// @notice Triggered when a donation has been made to the contract
    /// @param donater The address of the donater
    event DonateEvent(address indexed donater, uint amount);

    /// @notice Admin function to update the location at `index`
    /// @dev Create a new ImportantThings if `writeCount` % 10 == 0
    /// @param thing The important thing to store
    function write(string thing) external {
        
        if(writeCount % 10 == 0) {
            ImportantThings memory newContainer;
            newContainer.id = thingsList.length;
            thingsList.push(newContainer);
        }
        thingsList[thingsList.length-1].things[msg.sender] = thing;
        writeCount += 1;
        uint id = thingsList[thingsList.length-1].id;
        writeLog[msg.sender][id];
        dummy = !dummy;
        emit WriteEvent(msg.sender, id);
    }

    /// @notice Read a string stored by `address`
    /// @notice from the given container `id`
    /// @param id The container id
    /// @param account The address of the original writer
    /// @return A string from storage
    function read(uint id, address account) public view returns(string) {
        require(id < thingsList.length);
        return thingsList[id].things[account];
    }

    /// @notice Donate the message value to the pot
    function donate() public payable {
        donations += msg.value;
    }

    /// @notice Funds sent to the contract are considered donations
    function() public payable {
        donate();
    }

    /// @notice Withdrawal function for admin
    function withdraw() public onlyOwner {
        msg.sender.transfer(address(this).balance);
    }

    /// @notice Admin failsafe for destroying the contract
    function kill() onlyOwner public {
        selfdestruct(owner);
    }

}
