// Generated by the protocol buffer compiler.  DO NOT EDIT!
// source: entities.proto

package com.ververica.statefun.workshop.generated;

public interface TransactionOrBuilder extends
    // @@protoc_insertion_point(interface_extends:Transaction)
    com.google.protobuf.MessageOrBuilder {

  /**
   * <code>string account = 1;</code>
   */
  java.lang.String getAccount();
  /**
   * <code>string account = 1;</code>
   */
  com.google.protobuf.ByteString
      getAccountBytes();

  /**
   * <code>.google.protobuf.Timestamp timestamp = 2;</code>
   */
  boolean hasTimestamp();
  /**
   * <code>.google.protobuf.Timestamp timestamp = 2;</code>
   */
  com.google.protobuf.Timestamp getTimestamp();
  /**
   * <code>.google.protobuf.Timestamp timestamp = 2;</code>
   */
  com.google.protobuf.TimestampOrBuilder getTimestampOrBuilder();

  /**
   * <code>string merchant = 3;</code>
   */
  java.lang.String getMerchant();
  /**
   * <code>string merchant = 3;</code>
   */
  com.google.protobuf.ByteString
      getMerchantBytes();

  /**
   * <code>int32 amount = 4;</code>
   */
  int getAmount();
}